FROM node:20-alpine

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm install

# Copy application code
COPY . .

# Build
RUN npm run build

# Expose port
EXPOSE 3000

# Run with nginx or node (for production, use nginx)
CMD ["npm", "run", "preview"]
