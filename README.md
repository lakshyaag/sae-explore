# SAE Explorer

A tool for exploring AI-generated images by combining concepts with different stylistic features. This project allows you to generate and visualize how different artistic features affect various concepts.

## Components

### 1. Generation CLI (`main.py`)

A command-line tool for generating images by combining concepts with features at different strengths.

```bash
# Generate 3 variations of a "mountain landscape" with "mystical" features
uv run main.py generate "mountain landscape" "mystical" --variations 3 --min-strength 0.2 --max-strength 0.8

# List all discovered features related to "minimalist"
uv run main.py list-features "minimalist"
```

Options:

- `--variations/-n`: Number of strength variations to generate (default: 1)
- `--min-strength`: Minimum feature strength (-1 to 1, default: -0.5)
- `--max-strength`: Maximum feature strength (-1 to 1, default: 0.5)
- `--num-features/-f`: Number of top features to apply (1-5, default: 1)
- `--verbose/-v`: Enable verbose output

### 2. Visual Explorer (`app.py`)

A Streamlit web application for exploring and visualizing the generated images. Features include:

- Browse concepts and their associated features
- View images at different feature strengths
- See generated prompts and metadata
- Interactive strength slider for real-time exploration

```bash
# Run the web interface
uv run streamlit run app.py
```

## Setup

1. Clone the repository

```bash
git clone https://github.com/lakshyaag/sae-explore.git
cd sae-explore
```

2. Set up Supabase to persist generations and view them in Streamlit:

   1. Create a new project at [Supabase](https://supabase.com)
   2. Initialize the database schema:
      - Go to Database > SQL Editor
      - Copy the contents of `db.sql` from this repository
      - Run the SQL commands to create the required tables:
        - `concepts`: Stores the base concepts for image generation
        - `features`: Stores discovered features and their metadata
        - `generations`: Stores the generated images and their relationships

3. Create an account on [Goodfire](https://platform.goodfire.ai/landing)
4. Configure your image generation. By default, I'm using [Fal.ai](https://fal.ai/models/fal-ai/flux/schnell/api)
5. Set up environment variables in `.env`:

```env
GOODFIRE_API_KEY=your_goodfire_key
FAL_KEY=your_fal_key

SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=
SUPABASE_SERVICE_KEY=your_supabase_key
```

6. Install dependencies

```bash
uv sync
```

## Architecture

The project uses:

- Goodfire: For feature discovery and prompt enhancement
- Supabase: For storing concepts, features, and generations
- Fal.ai: For image generation
- Streamlit: For the web interface
- uv: God's answer to `poetry`

## License

MIT
