/**
 * Cliente HTTP central do frontend.
 *
 * Toda chamada à API passa por aqui. Criamos uma instância do Axios com a URL
 * base, um tempo limite e um "porteiro" (interceptor) que:
 * - no sucesso, entrega direto os dados (resposta.data), sem o envelope do
 *   Axios;
 * - no erro, entrega um ErroApi com mensagem em português.
 *
 * Assim as telas e os serviços nunca precisam lidar com detalhes do Axios.
 */

import axios from 'axios';

import { normalizarErro } from './erroApi.js';

/**
 * Remove barras sobrando no fim de uma URL.
 *
 * Por que existe: "http://x/" + "/rota" viraria "http://x//rota". Deixando a
 * base sem barra no final, os caminhos dos serviços começam com "/" e a URL
 * fica sempre correta.
 */
function semBarraNoFinal(url) {
  if (typeof url !== 'string') {
    return '';
  }
  return url.replace(/\/+$/, '');
}

/**
 * Cria uma instância configurada do Axios.
 *
 * Recebe:
 *   baseURL: endereço da API (ex.: "http://localhost:8000").
 *   timeout: tempo máximo de espera em milissegundos (padrão 20 s).
 *   adapter: opcional, usado só nos testes para simular respostas sem rede.
 *
 * Devolve: a instância do Axios pronta para uso.
 *
 * Exemplo: criarClienteApi({ baseURL: "http://localhost:8000" })
 */
export function criarClienteApi({ baseURL, timeout = 20000, adapter } = {}) {
  const cliente = axios.create({
    baseURL: semBarraNoFinal(baseURL),
    timeout,
    headers: { Accept: 'application/json' },
    // O adapter só entra na configuração quando foi informado. Nos testes ele
    // substitui a rede; em produção fica indefinido e o Axios usa o normal.
    ...(adapter ? { adapter } : {}),
  });

  // Interceptor de RESPOSTA: um "porteiro" que olha o resultado de toda
  // chamada antes de entregá-lo a quem pediu.
  cliente.interceptors.response.use(
    // Sucesso: devolvemos apenas os dados. Quem chama recebe o JSON direto.
    (resposta) => resposta.data,
    // Erro: convertemos para ErroApi e rejeitamos a promessa com ele.
    (erro) => Promise.reject(normalizarErro(erro)),
  );

  return cliente;
}

// import.meta.env é o objeto de variáveis do Vite. O "?." (optional chaining)
// evita erro quando este arquivo roda fora do Vite (testes com Node e o
// script de verificação), onde import.meta.env não existe.
const urlConfigurada = import.meta.env?.VITE_API_URL;

/**
 * Endereço da API usado pelo frontend.
 *
 * Vem de VITE_API_URL (arquivo frontend/.env) e, se estiver vazio ou ausente,
 * cai no padrão local "http://localhost:8000" para o projeto rodar sem
 * configuração extra.
 */
export const API_URL =
  typeof urlConfigurada === 'string' && urlConfigurada.trim() !== ''
    ? urlConfigurada.trim()
    : 'http://localhost:8000';

// Instância única usada pelos serviços (src/services/*.js).
export const api = criarClienteApi({ baseURL: API_URL });
