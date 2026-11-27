-- =====================================================================
-- Kültürİz güncelleme 5: gönderi düzenleme
-- Supabase panelinde: SQL Editor > New query > bu dosyanın tamamını yapıştır > Run
-- Birden fazla kez çalıştırmak güvenlidir.
-- =====================================================================

alter table public.gonderiler add column if not exists duzenlendi timestamptz;

-- Gönderi sahibi (kısıtlı değilse) kendi gönderisini, yönetici her gönderiyi düzenleyebilir.
drop policy if exists "gonderiler_guncelle" on public.gonderiler;
create policy "gonderiler_guncelle" on public.gonderiler for update to authenticated
  using ((kullanici_id = auth.uid() and public.aktif_uye()) or public.yonetici_mi())
  with check ((kullanici_id = auth.uid() and public.aktif_uye()) or public.yonetici_mi());
grant update (yer, konum, kategori, enlem, boylam, notu, medya) on public.gonderiler to authenticated;

-- Düzenlemede gönderinin sahibi, kimliği ve paylaşım tarihi değişmez; düzenlenme zamanı kaydedilir.
create or replace function public.gonderi_koru() returns trigger
language plpgsql as $$
begin
  new.id := old.id;
  new.kullanici_id := old.kullanici_id;
  new.olusturma := old.olusturma;
  new.duzenlendi := now();
  return new;
end $$;
drop trigger if exists gonderi_koru on public.gonderiler;
create trigger gonderi_koru before update on public.gonderiler for each row execute function public.gonderi_koru();

notify pgrst, 'reload schema';
