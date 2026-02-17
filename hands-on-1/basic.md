# Docker พื้นฐานและการปฏิบัติการ (Hands-on Workshop)

เอกสารฉบับนี้จัดทำขึ้นเพื่ออธิบายแนวคิดพื้นฐานของ Docker พร้อมแบบฝึกปฏิบัติที่ครอบคลุมการใช้งานในระดับเริ่มต้นจนถึงการประยุกต์ใช้เชิงระบบ (System-Level Usage) โดยเน้นความเข้าใจเชิงสถาปัตยกรรมและกระบวนการทำงานจริง

---

## 1. แนวคิดหลัก (Conceptual Model)

```
Dockerfile → Image → Container → Network → Volume → Runtime
```

คำอธิบายองค์ประกอบสำคัญ:

* **Dockerfile**: ชุดคำสั่งสำหรับสร้าง Image
* **Image**: ไฟล์ต้นแบบแบบ Immutable สำหรับสร้าง Container
* **Container**: อินสแตนซ์ที่ทำงานจริงของ Image
* **Volume**: กลไกสำหรับจัดเก็บข้อมูลแบบถาวร (Persistent Storage)
* **Network**: กลไกสำหรับการสื่อสารระหว่าง Container

ความเข้าใจลำดับการทำงานนี้เป็นพื้นฐานสำคัญของการออกแบบระบบที่ใช้ Container

---

## 2. คำสั่งพื้นฐานที่ใช้บ่อย (Core Commands)

### 2.1 การจัดการ Image

```bash
docker pull nginx
docker images
docker rmi nginx
```

### 2.2 วงจรชีวิตของ Container (Container Lifecycle)

```bash
docker run nginx
docker run -d -p 8080:80 --name mynginx nginx
docker ps
docker ps -a
docker stop mynginx
docker start mynginx
docker rm mynginx
```

### 2.3 การตรวจสอบและแก้ไขปัญหา (Inspect / Debug)

```bash
docker logs mynginx
docker exec -it mynginx sh
docker inspect mynginx
```

### 2.4 การจัดการ Volume

```bash
docker volume create myvolume
docker volume ls
docker run -v myvolume:/data alpine
```

### 2.5 การจัดการ Network

```bash
docker network ls
docker network create mynetwork
docker run --network mynetwork nginx
```

---

## 3. แบบฝึกปฏิบัติ (Hands-on Lab)

### Lab 1: การรัน Web Server

```bash
docker pull nginx
docker run -d -p 8080:80 --name webserver nginx
```

ทดสอบการทำงานผ่านเว็บเบราว์เซอร์ที่:

```
http://localhost:8080
```

วัตถุประสงค์:

* เข้าใจการทำ Port Mapping
* เข้าใจโหมดการทำงานแบบ Detached (-d)

---

### Lab 2: การเข้าสู่ Container

```bash
docker exec -it webserver sh
cd /usr/share/nginx/html
ls
```

วัตถุประสงค์:

* เข้าใจการเข้าถึง Runtime Environment
* ตรวจสอบโครงสร้างไฟล์ภายใน Container

---

### Lab 3: การจัดการข้อมูลแบบ Persistent ด้วย Volume

#### ขั้นตอนที่ 1: เตรียมไฟล์

```bash
mkdir mysite
echo "<h1>Hello Docker</h1>" > mysite/index.html
```

#### ขั้นตอนที่ 2: Mount Volume

```bash
docker run -d -p 8081:80 \
-v $(pwd)/mysite:/usr/share/nginx/html \
--name webserver2 nginx
```

ทดสอบที่:

```
http://localhost:8081
```

วัตถุประสงค์:

* เข้าใจการ Bind Mount
* เข้าใจแนวคิด Data Persistence

---

### Lab 4: การสร้าง Custom Image

#### สร้างไฟล์ Dockerfile

```dockerfile
FROM nginx
COPY mysite /usr/share/nginx/html
```

#### Build Image

```bash
docker build -t my-nginx .
```

#### Run Container จาก Image ที่สร้าง

```bash
docker run -d -p 8082:80 my-nginx
```

วัตถุประสงค์:

* เข้าใจขั้นตอน Build Image
* เข้าใจความแตกต่างระหว่าง Build-time และ Run-time

---

## 4. ตัวอย่างการทำงานแบบ Multi-Container

### สร้าง Network สำหรับ Application

```bash
docker network create appnet
```

### รันฐานข้อมูล

```bash
docker run -d \
--name postgres \
--network appnet \
-e POSTGRES_PASSWORD=1234 \
postgres
```

### รัน Backend และเชื่อมต่อฐานข้อมูล

```bash
docker run -d \
--name backend \
--network appnet \
-e DB_HOST=postgres \
my-backend-image
```

แนวคิดสำคัญ:

* Container สื่อสารกันผ่าน Docker Network
* ชื่อ Container สามารถใช้เป็น Hostname ภายใน Network เดียวกัน

---

## 5. การใช้งาน Docker Compose

### ตัวอย่างไฟล์ docker-compose.yml

```yaml
version: "3"

services:
  web:
    image: nginx
    ports:
      - "8080:80"

  db:
    image: postgres
    environment:
      POSTGRES_PASSWORD: 1234
```

### คำสั่งใช้งาน

```bash
docker compose up -d
docker compose down
```


