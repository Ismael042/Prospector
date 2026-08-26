create table leads (
  id uuid primary key default gen_random_uuid(),
  place_id text unique not null,
  name text not null,
  category text not null,
  location text not null,
  address text,
  phone text,
  rating numeric,
  review_count integer,
  maps_url text,
  stage text not null default 'found'
    check (stage in ('found', 'contacted', 'replied', 'meeting', 'closed', 'lost')),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index leads_stage_idx on leads (stage);
create index leads_category_idx on leads (category);
