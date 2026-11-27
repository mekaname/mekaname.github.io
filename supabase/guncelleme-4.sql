-- =====================================================================
-- Kültürize güncelleme 4: okul / şube / okul numarası, gönderi başına en fazla 7 dosya,
-- yeni ad (Kültürize)
-- Supabase panelinde: SQL Editor > New query > bu dosyanın tamamını yapıştır > Run
-- Birden fazla kez çalıştırmak güvenlidir.
-- =====================================================================

-- ---------- Okul bilgileri (yalnızca kişinin kendisi ve yönetici görür) ----------
alter table public.profiller add column if not exists okul text;
alter table public.profiller add column if not exists sube text;
alter table public.profiller add column if not exists okul_no text;
alter table public.profiller drop constraint if exists okul_gecerli;
alter table public.profiller add constraint okul_gecerli check (
  (okul is null or char_length(btrim(okul)) between 2 and 80)
  and (sube is null or char_length(btrim(sube)) between 1 and 10)
  and (okul_no is null or okul_no ~ '^[0-9]{1,8}$')
);
-- Herkese açık profil sütunları değişmedi; okul bilgileri listede yok, yani başkaları göremez.
grant update (okul, sube, okul_no) on public.profiller to authenticated;

-- Kişinin kendi gizli bilgileri
create or replace function public.benim_bilgilerim() returns json
language sql stable security definer set search_path = public as $$
  select json_build_object('dogum_tarihi', dogum_tarihi, 'okul', okul, 'sube', sube, 'okul_no', okul_no)
  from public.profiller where id = auth.uid();
$$;
revoke all on function public.benim_bilgilerim() from public, anon;
grant execute on function public.benim_bilgilerim() to authenticated;

-- ---------- Kayıt: doğum tarihi + okul bilgileri ----------
create or replace function public.yeni_kullanici() returns trigger
language plpgsql security definer set search_path = public as $$
declare d date; o text; s text; n text; m jsonb := coalesce(new.raw_user_meta_data, '{}'::jsonb);
begin
  begin
    d := nullif(m->>'dogum_tarihi', '')::date;
  exception when others then
    d := null;
  end;
  if d is not null and not public.yas_uygun(d) then
    raise exception 'Kültürize için en az 13 yaşında olmalısın.' using errcode = 'P0001';
  end if;
  o := nullif(btrim(coalesce(m->>'okul', '')), '');
  s := nullif(btrim(coalesce(m->>'sube', '')), '');
  n := nullif(btrim(coalesce(m->>'okul_no', '')), '');
  if o is not null and char_length(o) not between 2 and 80 then o := null; end if;
  if s is not null and char_length(s) > 10 then s := null; end if;
  if n is not null and n !~ '^[0-9]{1,8}$' then n := null; end if;
  insert into public.profiller (id, ad, foto_url, rol, dogum_tarihi, okul, sube, okul_no)
  values (
    new.id,
    left(coalesce(nullif(m->>'ad', ''), nullif(m->>'full_name', ''), nullif(m->>'name', ''), split_part(new.email, '@', 1)), 60),
    coalesce(m->>'avatar_url', ''),
    case when exists (select 1 from public.profiller where rol = 'admin') then 'uye' else 'admin' end,
    d, o, s, n
  )
  on conflict (id) do nothing;
  return new;
end $$;

-- Rol/kısıtlama yalnızca yönetici; doğum tarihi ve okul bilgileri bir kez girilir (yönetici düzeltebilir).
create or replace function public.profil_koru() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  if not public.yonetici_mi() then
    new.rol := old.rol;
    new.yasakli := old.yasakli;
    if old.dogum_tarihi is not null then new.dogum_tarihi := old.dogum_tarihi; end if;
    if old.okul is not null then new.okul := old.okul; end if;
    if old.sube is not null then new.sube := old.sube; end if;
    if old.okul_no is not null then new.okul_no := old.okul_no; end if;
  end if;
  if new.dogum_tarihi is distinct from old.dogum_tarihi and new.dogum_tarihi is not null and not public.yas_uygun(new.dogum_tarihi) then
    raise exception 'Kültürize için en az 13 yaşında olmalısın.' using errcode = 'P0001';
  end if;
  new.id := old.id;
  return new;
end $$;

-- Sansür okul ve şube alanlarını da kapsar.
create or replace function public.sansur_tetik() returns trigger
language plpgsql as $$
begin
  if tg_table_name = 'gonderiler' then
    new.yer := public.sansurle(new.yer); new.konum := public.sansurle(new.konum); new.notu := public.sansurle(new.notu);
  elsif tg_table_name = 'yorumlar' then
    new.metin := public.sansurle(new.metin);
  elsif tg_table_name = 'profiller' then
    new.ad := public.sansurle(new.ad); new.bio := public.sansurle(new.bio);
    new.okul := public.sansurle(new.okul); new.sube := public.sansurle(new.sube);
    new.ilgi_alanlari := coalesce((select array_agg(public.sansurle(x)) from unnest(new.ilgi_alanlari) x), '{}');
  elsif tg_table_name = 'sikayetler' then
    new.neden := public.sansurle(new.neden);
  end if;
  return new;
end $$;

-- Yönetici üye listesi: doğum tarihi ve okul bilgileriyle
drop function if exists public.yonetici_kullanicilar();
create function public.yonetici_kullanicilar()
returns table (id uuid, ad text, eposta text, rol text, yasakli boolean, olusturma timestamptz, gonderi int, yorum int,
               dogum_tarihi date, okul text, sube text, okul_no text)
language plpgsql stable security definer set search_path = public as $$
begin
  if not public.yonetici_mi() then
    raise exception 'Bu işlem için yönetici olmalısın' using errcode = '42501';
  end if;
  return query
    select p.id, p.ad, u.email::text, p.rol, p.yasakli, p.olusturma,
           (select count(*)::int from public.gonderiler g where g.kullanici_id = p.id),
           (select count(*)::int from public.yorumlar y where y.kullanici_id = p.id),
           p.dogum_tarihi, p.okul, p.sube, p.okul_no
    from public.profiller p join auth.users u on u.id = p.id
    order by p.olusturma desc;
end $$;
revoke all on function public.yonetici_kullanicilar() from public, anon;
grant execute on function public.yonetici_kullanicilar() to authenticated;

-- ---------- Gönderi başına en fazla 7 dosya ----------
create or replace function public.medya_gecerli(m jsonb, uid uuid) returns boolean
language sql immutable as $$
  select jsonb_typeof(m) = 'array'
     and jsonb_array_length(m) between 1 and 7
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

notify pgrst, 'reload schema';
