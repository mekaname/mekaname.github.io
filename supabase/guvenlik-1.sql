-- =====================================================================
-- Kültürize güvenlik güncellemesi 1
-- Supabase panelinde: SQL Editor > New query > bu dosyanın tamamını yapıştır > Run
-- Birden fazla kez çalıştırmak güvenlidir. (kurulum.sql'i yeni çalıştıranlar için de zararsızdır.)
-- =====================================================================

-- Gönderilerdeki medya adresleri yalnızca bu projenin "medya" deposunda,
-- gönderiyi paylaşan kişinin kendi klasöründe olabilir; 1-10 dosya.
create or replace function public.medya_gecerli(m jsonb, uid uuid) returns boolean
language sql immutable as $$
  select jsonb_typeof(m) = 'array'
     and jsonb_array_length(m) between 1 and 10
     and not exists (
       select 1 from jsonb_array_elements(m) e
       where not (
         jsonb_typeof(e) = 'object'
         and coalesce(e->>'tur', '') in ('foto', 'video')
         and coalesce(e->>'yol', '') like uid::text || '/%'
         and coalesce(e->>'url', '') like 'https://%.supabase.co/storage/v1/object/public/medya/' || uid::text || '/%'
         and coalesce(e->>'url', '') !~ '["''<>\s\\]'
       )
     );
$$;
alter table public.gonderiler drop constraint if exists medya_gecerli;
alter table public.gonderiler add constraint medya_gecerli check (public.medya_gecerli(medya, kullanici_id)) not valid;

-- Profil fotoğrafı: boş, bu projenin deposu ya da Google hesap fotoğrafı.
alter table public.profiller drop constraint if exists foto_url_gecerli;
alter table public.profiller add constraint foto_url_gecerli check (
  foto_url = ''
  or (foto_url ~ '^https://([a-z0-9-]+\.supabase\.co/storage/v1/object/public/medya/|[a-z0-9.-]+\.googleusercontent\.com/)'
      and foto_url !~ '["''<>\s\\]')
) not valid;

-- Toplu spam'e karşı günlük sınır: kişi başı 24 saatte en fazla 20 gönderi ve 200 yorum.
create or replace function public.gunluk_sinir() returns trigger
language plpgsql security definer set search_path = public as $$
declare n int;
begin
  if tg_table_name = 'gonderiler' then
    select count(*) into n from public.gonderiler where kullanici_id = new.kullanici_id and olusturma > now() - interval '24 hours';
    if n >= 20 then raise exception 'Günlük gönderi sınırına ulaştın (20). Yarın tekrar dene.' using errcode = 'P0001'; end if;
  else
    select count(*) into n from public.yorumlar where kullanici_id = new.kullanici_id and olusturma > now() - interval '24 hours';
    if n >= 200 then raise exception 'Günlük yorum sınırına ulaştın (200). Yarın tekrar dene.' using errcode = 'P0001'; end if;
  end if;
  return new;
end $$;
drop trigger if exists gunluk_sinir on public.gonderiler;
create trigger gunluk_sinir before insert on public.gonderiler for each row execute function public.gunluk_sinir();
drop trigger if exists gunluk_sinir on public.yorumlar;
create trigger gunluk_sinir before insert on public.yorumlar for each row execute function public.gunluk_sinir();
