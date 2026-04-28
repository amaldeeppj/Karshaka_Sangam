# Python MongoDB Docker Application

## Quick Start Guide

### 1. Clone the Repository

```bash
git clone https://github.com/amaldeeppj/Karshaka_Sangam.git
cd Karshaka_Sangam
```

### 2. Build the Docker Image

```bash
docker compose build
```

### 3. Start the Services

```bash
docker compose up -d
```

### 4. Stop the Services

```bash
docker compose down
```

---

## Additional Useful Commands

### Rebuild and Restart (when you make changes)

```bash
docker compose down -v
docker compose build --no-cache
docker compose up -d
```

### View Logs

```bash
# View app logs
docker compose logs -f app

# View MongoDB logs
docker compose logs -f mongo
```

### Stop and Remove Volumes (Reset everything)

```bash
docker compose down -v
```

## Services

- **app** → Runs on http://localhost:5000
- **mongodb** → Runs on port 27017

---

**Note**: Make sure you have Docker and Docker Compose installed before running the above commands.
```

---

