#!/usr/bin/env node
// webhook-receiver.js — Lightweight webhook server that converts HTTP events → OpenClaw wake
// Port: 9055
// POST /webhook { event, source, payload }
// POST /wake { text }
// GET /health

const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = 9055;
const LOG_FILE = '/tmp/webhook-receiver.log';
const CONFIG_FILE = path.join(process.env.HOME, '.openclaw/openclaw.json');
const OPENCLAW_URL = 'http://127.0.0.1:18789';

function log(msg) {
  const line = `[${new Date().toISOString()}] ${msg}\n`;
  process.stdout.write(line);
  fs.appendFileSync(LOG_FILE, line);
}

function getToken() {
  try {
    const config = JSON.parse(fs.readFileSync(CONFIG_FILE, 'utf8'));
    return config?.gateway?.auth?.token || '';
  } catch { return ''; }
}

const { execSync } = require('child_process');

async function wakeOpenClaw(text) {
  return new Promise((resolve, reject) => {
    try {
      const result = execSync(
        `/home/aiadmin/.npm-global/bin/openclaw system event --text ${JSON.stringify(text)} --mode next-heartbeat --json`,
        { timeout: 10000, encoding: 'utf8' }
      );
      resolve({ status: 200, body: result.trim() });
    } catch (err) {
      reject(new Error(err.stderr || err.message));
    }
  });
}

function parseBody(req) {
  return new Promise((resolve) => {
    let body = '';
    req.on('data', chunk => body += chunk);
    req.on('end', () => {
      try { resolve(JSON.parse(body)); }
      catch { resolve({}); }
    });
  });
}

const server = http.createServer(async (req, res) => {
  const url = req.url;
  const method = req.method;

  // CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Content-Type', 'application/json');

  if (method === 'GET' && url === '/health') {
    res.writeHead(200);
    res.end(JSON.stringify({ ok: true, service: 'webhook-receiver', port: PORT }));
    return;
  }

  if (method === 'POST' && (url === '/webhook' || url === '/wake')) {
    const body = await parseBody(req);
    const text = body.text || 
      `[webhook] ${body.source || 'external'}: ${body.event || 'event'} — ${JSON.stringify(body.payload || {}).slice(0, 100)}`;
    
    log(`Incoming: ${method} ${url} → "${text.slice(0, 80)}"`);
    
    try {
      const result = await wakeOpenClaw(text);
      log(`Wake result: ${result.status}`);
      res.writeHead(200);
      res.end(JSON.stringify({ ok: true, text, wake: result.status }));
    } catch (err) {
      log(`Wake error: ${err.message}`);
      res.writeHead(500);
      res.end(JSON.stringify({ ok: false, error: err.message }));
    }
    return;
  }

  res.writeHead(404);
  res.end(JSON.stringify({ ok: false, error: 'Not found' }));
});

server.listen(PORT, '127.0.0.1', () => {
  log(`webhook-receiver listening on 127.0.0.1:${PORT}`);
  log('Routes: GET /health | POST /webhook | POST /wake');
});

process.on('SIGTERM', () => { log('SIGTERM received, shutting down'); server.close(); });
process.on('SIGINT', () => { log('SIGINT received, shutting down'); server.close(); });
