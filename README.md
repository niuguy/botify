Botify is an AI agent bot builder for telegram. It allows you to build, test, serve and monitor your bots with ease. 

## Stack

- Django
- Postgress
- Docker compose

## Deployment on AWS EC2

### Prerequisites
- AWS EC2 instance running Ubuntu
- Docker and Docker Compose installed on EC2
- AWS CLI configured with appropriate permissions
- Domain name (optional)

### Deployment Steps
1. Clone the repository on your EC2 instance
2. Copy the `.env.example` to `.env` and update the variables
3. Run the deployment script:
   ```bash
   ./deploy.sh
   ```



