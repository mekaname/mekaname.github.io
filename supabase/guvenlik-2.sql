-- =====================================================================
-- Kültürize güvenlik güncellemesi 2: yaş sınırı, doğum tarihi gizliliği,
-- şikayetler, dosya listelemenin kapatılması
-- Supabase panelinde: SQL Editor > New query > bu dosyanın tamamını yapıştır > Run
-- Birden fazla kez çalıştırmak güvenlidir.
-- =====================================================================

-- ---------- Yaş sınırı (13) ----------
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
    raise exception 'Kültürize için en az 13 yaşında olmalısın.' using errcode = 'P0001';
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
    raise exception 'Kültürize için en az 13 yaşında olmalısın.' using errcode = 'P0001';
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

-- Supabase'in şema önbelleğini yenile (yeni sütun ve fonksiyonlar hemen görünsün)
notify pgrst, 'reload schema';
