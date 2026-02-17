###################################################
# Stage: base
#
# This base stage ensures all other stages are using the same base image
# and provides common configuration for all stages.
###################################################
FROM node:22 AS base
WORKDIR /usr/local/app

################## CLIENT STAGES ##################

###################################################
# Stage: client-base
#
# This stage is used as the base for the client-dev and client-build stages,
# since there are common steps needed for each.
###################################################
FROM base AS client-base
COPY client/package.json client/package-lock.json* ./
RUN npm install
COPY client/tsconfig.json ./
COPY client/vite.config.ts ./
COPY client/index.html ./
COPY client/src ./src

###################################################
# Stage: client-dev
#
# This stage is used for development of the client application. It sets
# the default command to start the Vite development server.
###################################################
FROM client-base AS client-dev
CMD ["npm", "run", "dev"]

###################################################
# Stage: client-build
#
# This stage builds the client application, producing static HTML, CSS, and
# JS files that can be served by the backend.
###################################################
FROM client-base AS client-build
RUN npm run build



################## BACKEND STAGES #################

###################################################
# Stage: backend-base
#
# This stage is used as the base for the backend-dev stage.
# Uses Python official image for the FastAPI backend.
###################################################
FROM python:3.12-slim AS backend-base
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python requirements and install dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application code including subdirectories
COPY backend/ .

# Expose port 8000 for FastAPI
EXPOSE 8000

# Default command for development
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]



###################################################
# Stage: backend-dev
#
# This stage is used for development of the backend application.
###################################################
FROM backend-base AS backend-dev



###################################################
# Stage: final
#
# This stage is intended to be the final "production" image.
# It sets up the backend and copies the built client application.
###################################################
FROM backend-base AS final
ENV NODE_ENV=production
COPY --from=client-build /usr/local/app/dist ./static
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
