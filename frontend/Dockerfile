# Development Dockerfile
FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./
COPY tsconfig.json ./
COPY next.config.js ./
COPY tailwind.config.ts ./
COPY postcss.config.js ./
COPY .eslintrc.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY app ./app
COPY public ./public 2>/dev/null || mkdir -p public

# Expose port
EXPOSE 3000

# Start development server with host binding for Docker
CMD ["npm", "run", "dev:docker"]
