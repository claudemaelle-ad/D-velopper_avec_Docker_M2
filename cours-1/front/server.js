const http = require("http");
const port = process.env.PORT || 3000;

http.createServer((req, res) => {
  if (req.url === "/health") {
    res.writeHead(200);
    return res.end("OK");
  }
  res.end("Hello world depuis le front Node.js !");
}).listen(port, () => console.log(`Front sur le port ${port}`));
