-- =====================================================================
-- Kültürİz güncelleme 8: video sınırı (dosya başına 15 MB) ve depolama temizliği
-- Supabase panelinde: SQL Editor > New query > bu dosyanın tamamını yapıştır > Run
-- Birden fazla kez çalıştırmak güvenlidir.
-- =====================================================================

-- Dosya başına en fazla 15 MB (fotoğraflar site tarafından zaten küçültülüyor).
update storage.buckets set file_size_limit = 15728640 where id = 'medya';

-- Yönetici için depolama durumu: toplam boyut, dosya sayısı ve hiçbir gönderi ya da
-- profil fotoğrafı tarafından kullanılmayan (silinmiş içeriklerden kalan) dosyalar.
-- Son 1 saatte yüklenen dosyalar, yükleme sürüyor olabileceği için listeye girmez.
create or replace function public.depolama_durumu() returns json
language plpgsql stable security definer set search_path = public, storage as $$
declare r json;
begin
  if not public.yonetici_mi() then
    raise exception 'Bu işlem için yönetici olmalısın' using errcode = '42501';
  end if;
  with kullanilan as (
    select e->>'yol' as yol
      from public.gonderiler g, jsonb_array_elements(case when jsonb_typeof(g.medya) = 'array' then g.medya else '[]'::jsonb end) e
     where e->>'yol' is not null
    union
    select substring(p.foto_url from '/storage/v1/object/public/medya/(.*)$')
      from public.profiller p
     where p.foto_url like '%/storage/v1/object/public/medya/%'
  ), dosyalar as (
    select o.name, coalesce((o.metadata->>'size')::bigint, 0) as boyut,
           (o.created_at < now() - interval '1 hour'
            and not exists (select 1 from kullanilan k where k.yol = o.name)) as yetim
      from storage.objects o
     where o.bucket_id = 'medya'
  )
  select json_build_object(
           'toplam', coalesce(sum(boyut), 0),
           'sayi', count(*),
           'yetim', coalesce((select json_agg(name) from (select name from dosyalar where yetim limit 1000) y), '[]'::json),
           'yetim_boyut', coalesce(sum(boyut) filter (where yetim), 0)
         )
    into r from dosyalar;
  return r;
end $$;
revoke all on function public.depolama_durumu() from public, anon;
grant execute on function public.depolama_durumu() to authenticated;

notify pgrst, 'reload schema';
