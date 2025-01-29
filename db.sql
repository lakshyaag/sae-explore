create table public.concepts (
  id uuid not null default extensions.uuid_generate_v4 (),
  created_at timestamp with time zone not null default now(),
  text text not null,
  constraint concepts_pkey primary key (id),
  constraint unique_concept unique (text)
) TABLESPACE pg_default;

create index IF not exists idx_concepts_text on public.concepts using btree (text) TABLESPACE pg_default;

create table public.features (
  id uuid not null default extensions.uuid_generate_v4 (),
  created_at timestamp with time zone not null default now(),
  input_text text not null,
  discovered_features jsonb not null,
  constraint features_pkey primary key (id),
  constraint unique_feature_input unique (input_text)
) TABLESPACE pg_default;

create index IF not exists idx_features_input_text on public.features using btree (input_text) TABLESPACE pg_default;

create table public.generations (
  id uuid not null default extensions.uuid_generate_v4 (),
  created_at timestamp with time zone not null default now(),
  concept_id uuid not null,
  feature_id uuid not null,
  feature_index integer not null,
  feature_strength double precision not null,
  generated_prompt text not null,
  image_url text null,
  constraint generations_pkey primary key (id),
  constraint generations_concept_id_fkey foreign KEY (concept_id) references concepts (id),
  constraint generations_feature_id_fkey foreign KEY (feature_id) references features (id)
) TABLESPACE pg_default;

create index IF not exists idx_generations_concept_id on public.generations using btree (concept_id) TABLESPACE pg_default;
create index IF not exists idx_generations_feature_id on public.generations using btree (feature_id) TABLESPACE pg_default;