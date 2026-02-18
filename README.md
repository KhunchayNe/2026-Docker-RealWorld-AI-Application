## ทำไมต้องใช้ Docker?

คำตอบสั้น: **เพื่อทำให้ซอฟต์แวร์รันได้เหมือนกันทุกที่ (Consistent, Portable, Reproducible Environment)**

คำตอบเชิงสถาปัตยกรรม: Docker คือ **runtime-level isolation** ที่ทำให้แอป + dependency ถูกแพ็กเป็น artifact เดียว (container image) แล้ว deploy ได้ deterministic

---

# 1) แก้ปัญหา “มันรันในเครื่องฉันได้” (Works on my machine)

ปัญหาคลาสสิก:

* Dev ใช้ Node 18
* Server ใช้ Node 16
* เครื่องหนึ่งใช้ OpenSSL คนละ version
* OS ต่างกัน (macOS vs Ubuntu)

Docker แก้โดย:

```
App + Runtime + Library + OS Layer → Docker Image
```

ทุก environment ใช้ image เดียวกัน → behavior เหมือนกัน

---

# 2) Isolation (แยก environment อย่างชัดเจน)

ไม่ต้องลง dependency ปนกันในเครื่อง:

```
Project A → Postgres 13
Project B → Postgres 16
Project C → Redis 7
```

รันพร้อมกันได้หมด
ไม่ชนกัน
ไม่ต้อง uninstall / reinstall

Docker ใช้ Linux namespaces + cgroups
→ แยก process, network, filesystem

---

# 3) Infrastructure as Code (Environment เป็นโค้ด)

แทนที่จะมี README แบบนี้:

```
1. Install Node
2. Install Postgres
3. Setup env
4. Seed database
5. Pray
```

คุณมี:

```dockerfile
FROM node:18
WORKDIR /app
COPY package*.json .
RUN npm install
COPY . .
CMD ["npm", "start"]
```

Environment = Declarative + Versioned + Git-controlled

---

# 4) เหมาะกับ Architecture แบบคุณ (SaaS / Microservices / System Design)

จาก tech stack คุณ:

* NestJS
* PostgreSQL
* React/Next.js
* Supabase
* Docker/K8s
* DevSecOps

Docker ช่วย:

| Use Case   | ประโยชน์                                 |
| ---------- | ---------------------------------------- |
| Local Dev  | Spin up ทั้งระบบด้วย `docker-compose up` |
| CI/CD      | Build → Test → Push Image                |
| Production | Deploy บน VPS / Cloud / K8s              |
| Scaling    | Replicate container ได้ง่าย              |

---

# 5) Docker ทำงานอย่างไร (Concept Model)

## Traditional VM

![Image](./images/container-vs-vm-inline1_tcm19-82163.png.jpeg)

### Machine Virtualization
* แต่ละ VM มี Guest OS
* กิน RAM หนัก
* Boot ช้า

### Docker Container
* แชร์ OS kernel
* เบากว่า VM มาก
* Start ภายในไม่กี่วินาที
* Layer-based image (efficient build cache)

---

# 6) Use Case เชิง Production (Architecture-first View)

### ตัวอย่าง SaaS (เช่น Smart Farm OS)

```
[NGINX]
    ↓
[API - NestJS] (container)
    ↓
[Postgres] (container)
    ↓
[Redis] (container)
```

คุณสามารถ:

* Scale API → 3 replicas
* Rollback version ได้ทันที
* Blue/Green deployment ได้

---

# 7) DevOps Flow แบบ Modern

```
Developer
   ↓
Docker Build
   ↓
Push to Registry
   ↓
Deploy (K8s / VPS / Cloud)
```

Artifact ที่ deploy = Docker Image
ไม่ใช่ source code

---

# 8) เมื่อไหร่ “ไม่จำเป็น” ต้องใช้ Docker?

* ทำ script เล็ก ๆ ใช้คนเดียว
* ทำ prototype เร็ว ๆ
* App ไม่มี dependency ซับซ้อน

แต่ถ้า:

* ทำ production
* ทำหลาย service
* ทำ SaaS
* ทำทีม

→ Docker ควรเป็น baseline


---

# สรุปแบบตรง ๆ

Docker ทำให้:

* Environment deterministic
* Deploy ง่าย
* Scale ง่าย
* CI/CD ทำงานจริง
* ลด human error
* Infrastructure กลายเป็น code

มันไม่ใช่แค่ “เครื่องมือรันแอป”
มันคือ “มาตรฐานการ deploy software ยุคใหม่”


