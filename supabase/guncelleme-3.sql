-- =====================================================================
-- Kültürİz güncelleme 3: uzun "Hakkımda" (250 kelime), uzun açıklama (700 kelime),
-- ilgi alanları (en fazla 3), küfür ve uygunsuz ifadelerin otomatik sansürü
-- Supabase panelinde: SQL Editor > New query > bu dosyanın tamamını yapıştır > Run
-- Birden fazla kez çalıştırmak güvenlidir.
-- =====================================================================

-- ---------- Uzunluk sınırları ----------
create or replace function public.kelime_sayisi(t text) returns int
language sql immutable as $$
  select coalesce(array_length(regexp_split_to_array(btrim(coalesce(t, '')), '\s+'), 1), 0) - case when btrim(coalesce(t, '')) = '' then 1 else 0 end;
$$;

alter table public.profiller drop constraint if exists profiller_bio_check;
alter table public.profiller drop constraint if exists bio_uzunluk;
alter table public.profiller add constraint bio_uzunluk check (char_length(bio) <= 2000 and public.kelime_sayisi(bio) <= 250);

alter table public.gonderiler drop constraint if exists gonderiler_notu_check;
alter table public.gonderiler drop constraint if exists notu_uzunluk;
alter table public.gonderiler add constraint notu_uzunluk check (char_length(notu) <= 5000 and public.kelime_sayisi(notu) <= 700);

-- ---------- İlgi alanları ----------
alter table public.profiller add column if not exists ilgi_alanlari text[] not null default '{}';
create or replace function public.ilgi_gecerli(a text[]) returns boolean
language sql immutable as $$
  select coalesce(cardinality(a), 0) <= 3
     and not exists (select 1 from unnest(coalesce(a, '{}')) x where char_length(btrim(x)) not between 1 and 30);
$$;
alter table public.profiller drop constraint if exists ilgi_alanlari_gecerli;
alter table public.profiller add constraint ilgi_alanlari_gecerli check (public.ilgi_gecerli(ilgi_alanlari));
grant select (ilgi_alanlari) on public.profiller to anon, authenticated;
grant update (ilgi_alanlari) on public.profiller to authenticated;

-- ---------- Sansür ----------
-- Kelimeler küçük harfe çevrilir (Türkçe kurallarıyla), rakam/simge hileleri (s1kt1r, @, $) çözülür,
-- tekrarlanan harfler teke indirilir (siiiiktir -> siktir). Eşleşen kelimenin ilk harfi kalır, gerisi yıldız olur.
create or replace function public.kufur_mu(w text) returns boolean
language plpgsql immutable as $$
declare n text;
begin
  n := replace(replace(w, 'İ', 'i'), 'I', 'ı');
  n := lower(n);
  n := translate(n, '0134@$5€', 'oieaasse');
  n := regexp_replace(n, '[^[:alpha:]]', '', 'g');
  n := regexp_replace(n, '(.)\1+', '\1', 'g');
  if n = '' then return false; end if;
  if n = any (array[
      'amk','amq','amg','aq','mk','mq','oç','oc','pç','sik','göt','götü','götler','pust','dick','dicks','pusy','fck','niga'
    ]) then return true; end if;
  return n ~ ('^(orospu|orosbu|oruspu|orspu|yarak|yarağ|dalyarak|dalyarağ|amına|amınak|aminak|amcık|amcik|amını|siktir|sikeyim|sikerim|sikiyim|sikim|sikik|sikiş|siker|sikti'
           || '|götün|götver|götlek|ibne|kahpe|pezevenk|pezo|puşt|gavat|kaltak|fahişe|fahise|sürtük|surtuk|yavşak|yavsak|şerefsiz|serefsiz|gerizekalı|gerizekali|taşak|tasak|piç'
           || '|fuck|shit|bitch|ashole|motherf|cunt|whore|slut|retard|porn)');
end $$;

create or replace function public.sansurle(t text) returns text
language plpgsql immutable as $$
declare parca text; sonuc text := '';
begin
  if t is null or t = '' then return t; end if;
  for parca in select (regexp_matches(t, '([^[:space:][:punct:]]+|[[:space:][:punct:]]+)', 'g'))[1] loop
    if parca !~ '^[[:space:][:punct:]]+$' and public.kufur_mu(parca) then
      sonuc := sonuc || left(parca, 1) || repeat('*', char_length(parca) - 1);
    else
      sonuc := sonuc || parca;
    end if;
  end loop;
  return sonuc;
end $$;

create or replace function public.sansur_tetik() returns trigger
language plpgsql as $$
begin
  if tg_table_name = 'gonderiler' then
    new.yer := public.sansurle(new.yer); new.konum := public.sansurle(new.konum); new.notu := public.sansurle(new.notu);
  elsif tg_table_name = 'yorumlar' then
    new.metin := public.sansurle(new.metin);
  elsif tg_table_name = 'profiller' then
    new.ad := public.sansurle(new.ad); new.bio := public.sansurle(new.bio);
    new.ilgi_alanlari := coalesce((select array_agg(public.sansurle(x)) from unnest(new.ilgi_alanlari) x), '{}');
  elsif tg_table_name = 'sikayetler' then
    new.neden := public.sansurle(new.neden);
  end if;
  return new;
end $$;
drop trigger if exists sansur on public.gonderiler;
create trigger sansur before insert or update on public.gonderiler for each row execute function public.sansur_tetik();
drop trigger if exists sansur on public.yorumlar;
create trigger sansur before insert or update on public.yorumlar for each row execute function public.sansur_tetik();
drop trigger if exists sansur on public.profiller;
create trigger sansur before insert or update on public.profiller for each row execute function public.sansur_tetik();
drop trigger if exists sansur on public.sikayetler;
create trigger sansur before insert or update on public.sikayetler for each row execute function public.sansur_tetik();

-- Mevcut içerikleri de sansürden geçir.
update public.gonderiler set yer = public.sansurle(yer), konum = public.sansurle(konum), notu = public.sansurle(notu)
  where yer <> public.sansurle(yer) or konum <> public.sansurle(konum) or notu <> public.sansurle(notu);
update public.yorumlar set metin = public.sansurle(metin) where metin <> public.sansurle(metin);
update public.profiller set ad = public.sansurle(ad), bio = public.sansurle(bio) where ad <> public.sansurle(ad) or bio <> public.sansurle(bio);

notify pgrst, 'reload schema';
