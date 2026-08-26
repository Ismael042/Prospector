alter table leads enable row level security;

create policy "Authenticated users can read leads"
  on leads for select
  to authenticated
  using (true);

create policy "Authenticated users can update leads"
  on leads for update
  to authenticated
  using (true)
  with check (true);
