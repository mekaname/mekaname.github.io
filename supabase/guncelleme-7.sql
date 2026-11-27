-- =====================================================================
-- Kültürİz güncelleme 7: "Haritada Bul" oyunu ve sıralama tablosu
-- Supabase panelinde: SQL Editor > New query > bu dosyanın tamamını yapıştır > Run
-- Birden fazla kez çalıştırmak güvenlidir.
-- =====================================================================

create table if not exists public.oyun_skorlari (
  id           uuid primary key default gen_random_uuid(),
  kullanici_id uuid not null references public.profiller(id) on delete cascade,
  mod          text not null check (mod in ('turkiye', 'dunya')),
  puan         int  not null check (puan between 0 and 5000),
  olusturma    timestamptz not null default now()
);
create index if not exists oyun_skorlari_mod_idx on public.oyun_skorlari (mod, puan desc);

alter table public.oyun_skorlari enable row level security;
drop policy if exists "oyun_oku" on public.oyun_skorlari;
create policy "oyun_oku" on public.oyun_skorlari for select to authenticated using (true);
drop policy if exists "oyun_ekle" on public.oyun_skorlari;
create policy "oyun_ekle" on public.oyun_skorlari for insert to authenticated
  with check (kullanici_id = auth.uid() and public.aktif_uye());
drop policy if exists "oyun_sil" on public.oyun_skorlari;
create policy "oyun_sil" on public.oyun_skorlari for delete to authenticated using (public.yonetici_mi());
revoke all on public.oyun_skorlari from anon;
grant select, insert, delete on public.oyun_skorlari to authenticated;

-- Günde en fazla 60 oyun kaydı; zaman sunucudan alınır.
create or replace function public.oyun_tetik() returns trigger
language plpgsql security definer set search_path = public as $$
declare n int;
begin
  select count(*) into n from public.oyun_skorlari where kullanici_id = new.kullanici_id and olusturma > now() - interval '24 hours';
  if n >= 60 then raise exception 'Bugünlük yeterince oynadın (60 oyun). Yarın tekrar dene.' using errcode = 'P0001'; end if;
  new.olusturma := now();
  return new;
end $$;
drop trigger if exists oyun_tetik on public.oyun_skorlari;
create trigger oyun_tetik before insert on public.oyun_skorlari for each row execute function public.oyun_tetik();

-- Sıralama: her oyuncunun en iyi puanı
create or replace function public.oyun_liderler(m text)
returns table (kullanici_id uuid, ad text, foto_url text, puan int)
language sql stable security definer set search_path = public as $$
  select p.id, p.ad, coalesce(p.foto_url, ''), max(s.puan)::int
  from public.oyun_skorlari s join public.profiller p on p.id = s.kullanici_id
  where s.mod = m and not p.yasakli
  group by p.id, p.ad, p.foto_url
  order by max(s.puan) desc, min(s.olusturma)
  limit 20;
$$;
revoke all on function public.oyun_liderler(text) from public, anon;
grant execute on function public.oyun_liderler(text) to authenticated;

notify pgrst, 'reload schema';
