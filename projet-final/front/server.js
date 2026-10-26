const http = require("http");
const fs = require("fs");
const path = require("path");

const port = process.env.PORT || 3000;
const page = fs.readFileSync(path.join(__dirname, "index.html"));

const server = http.createServer((req, res) => {
  if (req.url === "/health") {
    res.writeHead(200);
    return res.end("OK");
  }
  res.writeHead(200, { "Content-Type": "text/html; charset=utf-8" });
  res.end(page);
}).listen(port, () => console.log(`Front sur le port ${port}`));

// Arrêt propre quand Docker envoie SIGTERM
process.on("SIGTERM", () => server.close(() => process.exit(0)));