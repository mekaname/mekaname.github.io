-- =====================================================================
-- Mekaname veritabanı kurulumu
-- Supabase panelinde: SQL Editor > New query > bu dosyanın tamamını yapıştır > Run
-- Birden fazla kez çalıştırmak güvenlidir.
--
-- Önemli: Siteye İLK kayıt olan kişi otomatik olarak YÖNETİCİ (admin) olur.
-- Kurulumdan hemen sonra siteye ilk sen kayıt ol.
-- =====================================================================

-- ---------- Tablolar ----------
create table if not exists public.profiller (
  id         uuid primary key references auth.users(id) on delete cascade,
  ad         text not null default '' check (char_length(ad) <= 60),
  bio        text not null default '' check (char_length(bio) <= 150),
  foto_url   text not null default '',
  rol        text not null default 'uye' check (rol in ('uye', 'admin')),
  yasakli    boolean not null default false,
  olusturma  timestamptz not null default now()
);

create table if not exists public.gonderiler (
  id            uuid primary key default gen_random_uuid(),
  kullanici_id  uuid not null references public.profiller(id) on delete cascade,
  yer           text not null check (char_length(yer) between 2 and 80),
  konum         text not null default '' check (char_length(konum) <= 80),
  kategori      text not null default 'Diğer' check (char_length(kategori) <= 40),
  enlem         double precision not null check (enlem between -90 and 90),
  boylam        double precision not null check (boylam between -180 and 180),
  notu          text not null default '' check (char_length(notu) <= 500),
  medya         jsonb not null default '[]'::jsonb,
  olusturma     timestamptz not null default now()
);
create index if not exists gonderiler_olusturma_idx on public.gonderiler (olusturma desc);

-- gonderi_id metindir: örnek gönderiler ("efes" gibi) de beğenilip yorumlanabilsin diye.
create table if not exists public.begeniler (
  gonderi_id    text not null,
  kullanici_id  uuid not null references public.profiller(id) on delete cascade,
  olusturma     timestamptz not null default now(),
  primary key (gonderi_id, kullanici_id)
);
create table if not exists public.kayitlar (
  gonderi_id    text not null,
  kullanici_id  uuid not null references public.profiller(id) on delete cascade,
  olusturma     timestamptz not null default now(),
  primary key (gonderi_id, kullanici_id)
);
create table if not exists public.yorumlar (
  id            uuid primary key default gen_random_uuid(),
  gonderi_id    text not null,
  kullanici_id  uuid not null references public.profiller(id) on delete cascade,
  metin         text not null check (char_length(metin) between 1 and 500),
  olusturma     timestamptz not null default now()
);
create index if not exists yorumlar_gonderi_idx on public.yorumlar (gonderi_id, olusturma);

-- ---------- Yardımcı fonksiyonlar ----------
create or replace function public.yonetici_mi() returns boolean
language sql stable security definer set search_path = public as $$
  select exists (select 1 from public.profiller where id = auth.uid() and rol = 'admin');
$$;

create or replace function public.aktif_uye() returns boolean
language sql stable security definer set search_path = public as $$
  select exists (select 1 from public.profiller where id = auth.uid() and not yasakli);
$$;

-- Yeni kayıt olan herkese profil açılır; hiç yönetici yoksa ilk kişi yönetici olur.
create or replace function public.yeni_kullanici() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  insert into public.profiller (id, ad, foto_url, rol)
  values (
    new.id,
    left(coalesce(nullif(new.raw_user_meta_data->>'ad', ''), nullif(new.raw_user_meta_data->>'full_name', ''),
                  nullif(new.raw_user_meta_data->>'name', ''), split_part(new.email, '@', 1)), 60),
    coalesce(new.raw_user_meta_data->>'avatar_url', ''),
    case when exists (select 1 from public.profiller where rol = 'admin') then 'uye' else 'admin' end
  )
  on conflict (id) do nothing;
  return new;
end $$;
drop trigger if exists yeni_kullanici on auth.users;
create trigger yeni_kullanici after insert on auth.users
  for each row execute function public.yeni_kullanici();

-- Üyeler kendi rolünü ya da kısıtlamasını değiştiremez; bunu yalnızca yönetici yapar.
create or replace function public.profil_koru() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  if not public.yonetici_mi() then
    new.rol := old.rol;
    new.yasakli := old.yasakli;
  end if;
  new.id := old.id;
  return new;
end $$;
drop trigger if exists profil_koru on public.profiller;
create trigger profil_koru before update on public.profiller
  for each row execute function public.profil_koru();

-- Gönderi silinince ona ait beğeni, kayıt ve yorumlar da silinir.
create or replace function public.gonderi_temizle() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  delete from public.begeniler where gonderi_id = old.id::text;
  delete from public.kayitlar  where gonderi_id = old.id::text;
  delete from public.yorumlar  where gonderi_id = old.id::text;
  return old;
end $$;
drop trigger if exists gonderi_temizle on public.gonderiler;
create trigger gonderi_temizle after delete on public.gonderiler
  for each row execute function public.gonderi_temizle();

-- ---------- Satır düzeyi güvenlik (kim neyi görür, kim neyi değiştirir) ----------
alter table public.profiller  enable row level security;
alter table public.gonderiler enable row level security;
alter table public.begeniler  enable row level security;
alter table public.kayitlar   enable row level security;
alter table public.yorumlar   enable row level security;

drop policy if exists "profiller_oku" on public.profiller;
create policy "profiller_oku" on public.profiller for select using (true);
drop policy if exists "profiller_guncelle" on public.profiller;
create policy "profiller_guncelle" on public.profiller for update
  using (id = auth.uid() or public.yonetici_mi()) with check (id = auth.uid() or public.yonetici_mi());

drop policy if exists "gonderiler_oku" on public.gonderiler;
create policy "gonderiler_oku" on public.gonderiler for select using (true);
drop policy if exists "gonderiler_ekle" on public.gonderiler;
create policy "gonderiler_ekle" on public.gonderiler for insert to authenticated
  with check (kullanici_id = auth.uid() and public.aktif_uye());
drop policy if exists "gonderiler_sil" on public.gonderiler;
create policy "gonderiler_sil" on public.gonderiler for delete to authenticated
  using (kullanici_id = auth.uid() or public.yonetici_mi());

drop policy if exists "begeniler_oku" on public.begeniler;
create policy "begeniler_oku" on public.begeniler for select using (true);
drop policy if exists "begeniler_ekle" on public.begeniler;
create policy "begeniler_ekle" on public.begeniler for insert to authenticated
  with check (kullanici_id = auth.uid() and public.aktif_uye());
drop policy if exists "begeniler_sil" on public.begeniler;
create policy "begeniler_sil" on public.begeniler for delete to authenticated using (kullanici_id = auth.uid());

drop policy if exists "kayitlar_oku" on public.kayitlar;
create policy "kayitlar_oku" on public.kayitlar for select to authenticated using (kullanici_id = auth.uid());
drop policy if exists "kayitlar_ekle" on public.kayitlar;
create policy "kayitlar_ekle" on public.kayitlar for insert to authenticated with check (kullanici_id = auth.uid());
drop policy if exists "kayitlar_sil" on public.kayitlar;
create policy "kayitlar_sil" on public.kayitlar for delete to authenticated using (kullanici_id = auth.uid());

drop policy if exists "yorumlar_oku" on public.yorumlar;
create policy "yorumlar_oku" on public.yorumlar for select using (true);
drop policy if exists "yorumlar_ekle" on public.yorumlar;
create policy "yorumlar_ekle" on public.yorumlar for insert to authenticated
  with check (kullanici_id = auth.uid() and public.aktif_uye());
drop policy if exists "yorumlar_sil" on public.yorumlar;
create policy "yorumlar_sil" on public.yorumlar for delete to authenticated
  using (kullanici_id = auth.uid() or public.yonetici_mi());

-- ---------- Beğeni ve yorum sayıları ----------
create or replace view public.gonderi_sayilari with (security_invoker = on) as
  select gonderi_id, sum(b)::int as begeni, sum(y)::int as yorum
  from (select gonderi_id, 1 as b, 0 as y from public.begeniler
        union all
        select gonderi_id, 0, 1 from public.yorumlar) t
  group by gonderi_id;
grant select on public.gonderi_sayilari to anon, authenticated;

-- ---------- Yönetici: üye listesi (e-postalar yalnızca yöneticiye görünür) ----------
create or replace function public.yonetici_kullanicilar()
returns table (id uuid, ad text, eposta text, rol text, yasakli boolean, olusturma timestamptz, gonderi int, yorum int)
language plpgsql stable security definer set search_path = public as $$
begin
  if not public.yonetici_mi() then
    raise exception 'Bu işlem için yönetici olmalısın' using errcode = '42501';
  end if;
  return query
    select p.id, p.ad, u.email::text, p.rol, p.yasakli, p.olusturma,
           (select count(*)::int from public.gonderiler g where g.kullanici_id = p.id),
           (select count(*)::int from public.yorumlar y where y.kullanici_id = p.id)
    from public.profiller p join auth.users u on u.id = p.id
    order by p.olusturma desc;
end $$;
revoke all on function public.yonetici_kullanicilar() from public, anon;
grant execute on function public.yonetici_kullanicilar() to authenticated;

-- ---------- Fotoğraf ve video deposu ----------
-- Herkes görebilir; üyeler yalnızca kendi klasörlerine (kullanıcı kimliği) yükleyebilir. Dosya başına en fazla 50 MB.
insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values ('medya', 'medya', true, 52428800, array['image/jpeg', 'image/png', 'image/webp', 'image/gif', 'video/mp4', 'video/quicktime', 'video/webm'])
on conflict (id) do update set public = true, file_size_limit = excluded.file_size_limit, allowed_mime_types = excluded.allowed_mime_types;

drop policy if exists "medya_oku" on storage.objects;
create policy "medya_oku" on storage.objects for select using (bucket_id = 'medya');
drop policy if exists "medya_yukle" on storage.objects;
create policy "medya_yukle" on storage.objects for insert to authenticated
  with check (bucket_id = 'medya' and (storage.foldername(name))[1] = auth.uid()::text and public.aktif_uye());
drop policy if exists "medya_sil" on storage.objects;
create policy "medya_sil" on storage.objects for delete to authenticated
  using (bucket_id = 'medya' and ((storage.foldername(name))[1] = auth.uid()::text or public.yonetici_mi()));

-- ---------- Gerekirse: bir hesabı elle yönetici yapmak ----------
-- update public.profiller set rol = 'admin'
--   where id = (select id from auth.users where email = 'SENIN@EPOSTAN.com');

-- ---------- Güvenlik kuralları (supabase/guvenlik-1.sql ile aynı) ----------
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

-- ---------- Güvenlik güncellemesi 2 (supabase/guvenlik-2.sql ile aynı) ----------
alter table public.profiller add column if not exists dogum_tarihi date;

create or replace function public.yas_uygun(d date) returns boolean
language sql stable as $$
  select d is not null and d >= date '1900-01-01' and d <= (current_date - interval '13 years')::date;
$$;

-- Yeni kayıtta doğum tarihi verildiyse 13 yaş kontrolü; ilk kayıt olan yönetici olur.
create or replace function public.yeni_kullanici() returns trigger
language plpgsql security definer set search_path = public as $$
declare d date;
begin
  begin
    d := nullif(new.raw_user_meta_data->>'dogum_tarihi', '')::date;
  exception when others then
    d := null;
  end;
  if d is not null and not public.yas_uygun(d) then
    raise exception 'Mekaname için en az 13 yaşında olmalısın.' using errcode = 'P0001';
  end if;
  insert into public.profiller (id, ad, foto_url, rol, dogum_tarihi)
  values (
    new.id,
    left(coalesce(nullif(new.raw_user_meta_data->>'ad', ''), nullif(new.raw_user_meta_data->>'full_name', ''),
                  nullif(new.raw_user_meta_data->>'name', ''), split_part(new.email, '@', 1)), 60),
    coalesce(new.raw_user_meta_data->>'avatar_url', ''),
    case when exists (select 1 from public.profiller where rol = 'admin') then 'uye' else 'admin' end,
    d
  )
  on conflict (id) do nothing;
  return new;
end $$;

-- Üyeler rolünü/kısıtlamasını değiştiremez; doğum tarihi bir kez girilir ve sonra değiştirilemez.
create or replace function public.profil_koru() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  if not public.yonetici_mi() then
    new.rol := old.rol;
    new.yasakli := old.yasakli;
    if old.dogum_tarihi is not null then
      new.dogum_tarihi := old.dogum_tarihi;
    end if;
  end if;
  if new.dogum_tarihi is distinct from old.dogum_tarihi and new.dogum_tarihi is not null and not public.yas_uygun(new.dogum_tarihi) then
    raise exception 'Mekaname için en az 13 yaşında olmalısın.' using errcode = 'P0001';
  end if;
  new.id := old.id;
  return new;
end $$;

-- Paylaşım, yorum ve beğeni için: kısıtlı olmamak ve yaş şartını karşılamak gerekir.
create or replace function public.aktif_uye() returns boolean
language sql stable security definer set search_path = public as $$
  select exists (select 1 from public.profiller where id = auth.uid() and not yasakli and public.yas_uygun(dogum_tarihi));
$$;

-- Doğum tarihi herkese açık profil bilgisinde görünmez; kişi yalnızca kendi tarihini okuyabilir.
revoke select on public.profiller from anon, authenticated;
grant select (id, ad, bio, foto_url, rol, yasakli, olusturma) on public.profiller to anon, authenticated;
revoke update on public.profiller from anon, authenticated;
grant update (ad, bio, foto_url, dogum_tarihi, rol, yasakli) on public.profiller to authenticated;

create or replace function public.benim_dogum_tarihim() returns date
language sql stable security definer set search_path = public as $$
  select dogum_tarihi from public.profiller where id = auth.uid();
$$;
revoke all on function public.benim_dogum_tarihim() from public, anon;
grant execute on function public.benim_dogum_tarihim() to authenticated;

-- ---------- Şikayetler ----------
create table if not exists public.sikayetler (
  id            uuid primary key default gen_random_uuid(),
  gonderi_id    text not null,
  kullanici_id  uuid not null references public.profiller(id) on delete cascade,
  neden         text not null check (char_length(neden) between 1 and 300),
  olusturma     timestamptz not null default now(),
  unique (gonderi_id, kullanici_id)
);
alter table public.sikayetler enable row level security;
drop policy if exists "sikayetler_ekle" on public.sikayetler;
create policy "sikayetler_ekle" on public.sikayetler for insert to authenticated
  with check (kullanici_id = auth.uid() and public.aktif_uye());
drop policy if exists "sikayetler_oku" on public.sikayetler;
create policy "sikayetler_oku" on public.sikayetler for select to authenticated using (public.yonetici_mi());
drop policy if exists "sikayetler_sil" on public.sikayetler;
create policy "sikayetler_sil" on public.sikayetler for delete to authenticated using (public.yonetici_mi());
grant select, insert, delete on public.sikayetler to authenticated;

-- Gönderi silinince şikayetleri de silinir.
create or replace function public.gonderi_temizle() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  delete from public.begeniler  where gonderi_id = old.id::text;
  delete from public.kayitlar   where gonderi_id = old.id::text;
  delete from public.yorumlar   where gonderi_id = old.id::text;
  delete from public.sikayetler where gonderi_id = old.id::text;
  return old;
end $$;

-- ---------- Dosya deposu: listeleme kapalı ----------
-- Fotoğraf ve videolar herkese açık adresleriyle görünmeye devam eder; ama kimse depodaki dosyaların listesini çekemez.
drop policy if exists "medya_oku" on storage.objects;
create policy "medya_oku" on storage.objects for select to authenticated
  using (bucket_id = 'medya' and ((storage.foldername(name))[1] = auth.uid()::text or public.yonetici_mi()));
