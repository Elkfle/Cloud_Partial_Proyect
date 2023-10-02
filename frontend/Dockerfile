# Usar una imagen oficial de Node.js como base
FROM node:20

# Establecer el directorio de trabajo en el contenedor
WORKDIR /app

# Copiar package.json y package-lock.json al directorio de trabajo
COPY package*.json ./

# Instalar las dependencias del proyecto
RUN npm install

# Copiar el resto de los archivos del proyecto al contenedor
COPY . .

# Compilar la aplicación para producción
RUN npm run build

# Usar un servidor simple para servir el contenido estático
FROM nginx:alpine
COPY --from=0 /app/dist /usr/share/nginx/html

# Exponer el puerto 80
EXPOSE 8080

# Iniciar el servidor nginx
CMD ["nginx", "-g", "daemon off;"]
