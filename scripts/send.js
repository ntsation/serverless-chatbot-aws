// send.js
require('dotenv').config({ path: '../.env' });
const fetch = require('node-fetch');

const URL_API_ID = process.env.APPSYNC_API_ID;
const REGION = process.env.AWS_REGION;
const API_KEY = process.env.APPSYNC_API_KEY;


const MUTATION = `
mutation SendMessage($chatId: ID!, $content: String!) {
  sendMessage(chatId: $chatId, content: $content) {
    id
    chatId
    userId
    role
    content
    createdAt
  }
}
`;

const VARIABLES = {
  chatId: process.env.CHAT_ID || '',
  content: process.env.MESSAGE_CONTENT || 'Mensagem de teste',
};

const url = `https://${URL_API_ID}.appsync-api.${REGION}.amazonaws.com/graphql`;

(async () => {
  try {
    const res = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': API_KEY,
      },
      body: JSON.stringify({
        query: MUTATION,
        variables: VARIABLES,
      }),
    });

    const data = await res.json();
    console.log('✅ Resposta da mutation:', data);
  } catch (err) {
    console.error('❌ Erro ao enviar mensagem:', err);
  }
})();
