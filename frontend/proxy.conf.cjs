// El proxy evita escribir la dirección del backend en los servicios Angular.
const target = process.env.API_PROXY_TARGET;
if (!target) throw new Error('Define API_PROXY_TARGET con la dirección de FastAPI.');
module.exports = { '/api/**': { target, secure: false } };
