alter table leads
  add column landing_html text,
  add column email_subject text,
  add column email_body text,
  add column call_script text,
  add column preview_published boolean not null default false,
  add column preview_url text;
