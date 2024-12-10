
---

# Flask Application Deployment on AWS EC2 with Docker and Nginx

This guide provides step-by-step instructions to deploy a Flask application using Docker, hosted on an AWS EC2 instance, with a custom domain (`tecloud.fun`) and HTTPS enabled via Nginx and Certbot.

---

## Prerequisites
- **AWS EC2 instance** with Ubuntu (or similar) as the OS.
- **Domain** registered (e.g., `tecloud.fun`).
- **Dockerized Flask application** pushed to Docker Hub.
- SSH access to your EC2 instance.

---

## Steps for Deployment

### **1. Set Up AWS EC2 Instance**
1. Log in to your AWS Console and navigate to **EC2**.
2. Launch a new instance with the following configuration:
   - **AMI**: Ubuntu 20.04 LTS.
   - **Instance Type**: `t2.micro` (or as per your needs).
   - **Key Pair**: Use an existing or create a new key pair.
   - **Security Group**: Allow:
     - **SSH (port 22)**
     - **HTTP (port 80)**
     - **HTTPS (port 443)**
   - **Storage**: Set disk size (e.g., 10–20 GB).

3. Launch the instance and note its **public IP address**.

### **2. Connect to Your Instance**
Use SSH to access the instance:
```bash
ssh -i your-key.pem ubuntu@your-ec2-public-ip
```

### **3. Install Docker**
Run the following commands to install Docker:
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install docker.io -y
sudo systemctl start docker
sudo systemctl enable docker
```

### **4. Pull and Run Your Dockerized Flask Application**
1. Pull the Docker image from Docker Hub:
   ```bash
   docker pull your_dockerhub_username/your_image_name:tag
   ```
2. Run the Docker container:
   ```bash
   docker run -d -p 5000:5000 your_dockerhub_username/your_image_name:tag
   ```

### **5. Configure Your Domain**
1. Log in to your domain registrar's dashboard.
2. Update the **DNS A record** to point to your EC2 public IP:
   - **Type**: A
   - **Host**: `@` (or `www` for subdomains)
   - **Value**: Your EC2 instance's public IP address.
   - **TTL**: 1 hour (or as low as allowed).

### **6. Install and Configure Nginx**
1. Install Nginx:
   ```bash
   sudo apt install nginx -y
   ```
2. Create a new configuration file for your domain:
   ```bash
   sudo nano /etc/nginx/sites-available/tecloud.fun
   ```
3. Add the following configuration:
   ```nginx
   server {
       listen 80;
       server_name tecloud.fun www.tecloud.fun;

       location / {
           proxy_pass http://localhost:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```
4. Enable the configuration:
   ```bash
   sudo ln -s /etc/nginx/sites-available/tecloud.fun /etc/nginx/sites-enabled/
   sudo nginx -t  # Test the Nginx configuration
   sudo systemctl restart nginx
   ```
5. Allow HTTP traffic in AWS Security Groups.

### **7. Secure Your Site with HTTPS**
1. Install Certbot for SSL certificates:
   ```bash
   sudo apt install certbot python3-certbot-nginx -y
   ```
2. Obtain and configure the SSL certificate:
   ```bash
   sudo certbot --nginx -d tecloud.fun -d www.tecloud.fun
   ```
3. Verify automatic renewal:
   ```bash
   sudo certbot renew --dry-run
   ```

### **8. Test Your Deployment**
1. Visit your domain (`http://tecloud.fun` or `https://tecloud.fun`).
2. Verify that the application is running and HTTPS is active.

---

## Troubleshooting
- **DNS Propagation Delay**: DNS changes may take up to 24 hours to propagate.
- **Firewall Issues**: Ensure the Security Group allows inbound traffic on ports 80 (HTTP) and 443 (HTTPS).
- **Docker Issues**: Check container logs if the app doesn't start:
  ```bash
  docker logs container_id
  ```

---

## Author
**Asif**  
Deployed with love and Flask 💻.
