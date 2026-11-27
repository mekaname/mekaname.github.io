-- =====================================================================
-- Kültürİz güncelleme 6: kullanıcılar arası mesajlaşma ve gönderi paylaşma
-- Supabase panelinde: SQL Editor > New query > bu dosyanın tamamını yapıştır > Run
-- Birden fazla kez çalıştırmak güvenlidir.
-- =====================================================================

create table if not exists public.mesajlar (
  id          uuid primary key default gen_random_uuid(),
  gonderen_id uuid not null references public.profiller(id) on delete cascade,
  alici_id    uuid not null references public.profiller(id) on delete cascade,
  gonderi_id  text,
  metin       text not null default '' check (char_length(metin) <= 1000),
  okundu      boolean not null default false,
  olusturma   timestamptz not null default now(),
  check (gonderen_id <> alici_id),
  check (gonderi_id is not null or char_length(btrim(metin)) > 0)
);
create index if not exists mesajlar_alici_idx on public.mesajlar (alici_id, olusturma desc);
create index if not exists mesajlar_gonderen_idx on public.mesajlar (gonderen_id, olusturma desc);

-- Mesajları yalnızca gönderen ve alan görür (yönetici dahil başka kimse göremez).
alter table public.mesajlar enable row level security;
drop policy if exists "mesajlar_oku" on public.mesajlar;
create policy "mesajlar_oku" on public.mesajlar for select to authenticated
  using (auth.uid() in (gonderen_id, alici_id));
drop policy if exists "mesajlar_gonder" on public.mesajlar;
create policy "mesajlar_gonder" on public.mesajlar for insert to authenticated
  with check (gonderen_id = auth.uid() and public.aktif_uye());
-- Alan kişi yalnızca "okundu" bilgisini değiştirebilir.
drop policy if exists "mesajlar_okundu" on public.mesajlar;
create policy "mesajlar_okundu" on public.mesajlar for update to authenticated
  using (alici_id = auth.uid()) with check (alici_id = auth.uid());
revoke update on public.mesajlar from anon, authenticated;
grant update (okundu) on public.mesajlar to authenticated;
grant select, insert on public.mesajlar to authenticated;
drop policy if exists "mesajlar_sil" on public.mesajlar;
create policy "mesajlar_sil" on public.mesajlar for delete to authenticated using (gonderen_id = auth.uid());
grant delete on public.mesajlar to authenticated;

-- Sansür ve günlük sınır (kişi başı 24 saatte 300 mesaj)
create or replace function public.mesaj_tetik() returns trigger
language plpgsql security definer set search_path = public as $$
declare n int;
begin
  if tg_op = 'INSERT' then
    select count(*) into n from public.mesajlar where gonderen_id = new.gonderen_id and olusturma > now() - interval '24 hours';
    if n >= 300 then raise exception 'Günlük mesaj sınırına ulaştın (300). Yarın tekrar dene.' using errcode = 'P0001'; end if;
    new.metin := public.sansurle(new.metin);
    new.okundu := false;
    new.olusturma := now();
  end if;
  return new;
end $$;
drop trigger if exists mesaj_tetik on public.mesajlar;
create trigger mesaj_tetik before insert on public.mesajlar for each row execute function public.mesaj_tetik();

notify pgrst, 'reload schema';
