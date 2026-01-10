# Household Items Image Generation

This script now supports **3 different image generation providers** to give you flexibility in quality and cost:

## Supported Providers

### 1. OpenAI DALL-E 3 (Recommended)
- **Quality**: Excellent
- **Resolution**: 1024x1024
- **Cost**: ~$0.04 per image
- **Speed**: ~5-10 seconds per image
- **Setup**: Add `OPENAI_API_KEY` to `.env` file

**To use:**
```bash
python scripts/generate_household_icons.py --provider openai --force
```

### 2. Stability AI SD3
- **Quality**: Very Good
- **Resolution**: 512x512
- **Cost**: ~$0.006 per image
- **Speed**: ~3-5 seconds per image
- **Setup**: Add `STABILITY_API_KEY` to `.env` file

**To use:**
```bash
python scripts/generate_household_icons.py --provider stability --force
```

### 3. Replicate SDXL
- **Quality**: Very Good
- **Resolution**: 1024x1024
- **Cost**: ~$0.002-0.03 per image
- **Speed**: ~10-30 seconds per image (includes polling)
- **Setup**: Add `REPLICATE_API_TOKEN` to `.env` file

**To use:**
```bash
python scripts/generate_household_icons.py --provider replicate --force
```

## Quick Start

### Option 1: Use OpenAI (Best Quality)
```bash
# Add your API key to .env
echo "OPENAI_API_KEY=sk-your-key-here" >> .env

# Generate all icons
python scripts/generate_household_icons.py --provider openai --force
```

### Option 2: Use Replicate (Most Cost-Effective)
```bash
# Add your API token to .env
echo "REPLICATE_API_TOKEN=r8_your-token-here" >> .env

# Generate all icons
python scripts/generate_household_icons.py --provider replicate --force
```

## Commands

```bash
# Test without generating (dry run)
python scripts/generate_household_icons.py --provider openai --dry-run

# Generate specific items only
python scripts/generate_household_icons.py --provider openai --items spoon,fork,knife

# Regenerate all existing icons
python scripts/generate_household_icons.py --provider openai --force

# Use different providers
python scripts/generate_household_icons.py --provider stability --force
python scripts/generate_household_icons.py --provider replicate --force
```

## Getting API Keys

### OpenAI API Key
1. Go to https://platform.openai.com/api-keys
2. Create a new API key
3. Copy the key and add to `.env`:
   ```
   OPENAI_API_KEY=sk-your-key-here
   ```

### Replicate API Token
1. Go to https://replicate.com/account/api-tokens
2. Create a new token
3. Copy the token and add to `.env`:
   ```
   REPLICATE_API_TOKEN=r8_your-token-here
   ```

### Stability AI API Key
1. Go to https://platform.stability.ai/account/keys
2. Create a new API key
3. Copy the key and add to `.env`:
   ```
   STABILITY_API_KEY=sk-your-key-here
   ```

## Cost Comparison for 167 Icons

| Provider | Cost per Image | Total Cost |
|----------|-----------------|-------------|
| OpenAI DALL-E 3 | ~$0.04 | ~$6.68 |
| Stability SD3 | ~$0.006 | ~$1.00 |
| Replicate SDXL | ~$0.002-0.03 | ~$0.33-$5.01 |

## Recommended Approach

1. **For best quality**: Use OpenAI DALL-E 3
2. **For lowest cost**: Use Replicate SDXL
3. **For balance**: Use Stability AI SD3

The current icons already generated (32 items) used Stability AI. You can regenerate all 167 items with any provider using the `--force` flag.
