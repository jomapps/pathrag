module.exports = {
  apps: [{
    name: 'pathrag-api',
    script: './start_pathrag.sh',
    interpreter: 'bash',
    cwd: '/opt/pathrag/pathrag',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    env: {
      NODE_ENV: 'production',
      FLASK_ENV: 'production'
    },
    error_file: './logs/pathrag-error.log',
    out_file: './logs/pathrag-out.log',
    log_file: './logs/pathrag-combined.log',
    time: true
  }]
};
