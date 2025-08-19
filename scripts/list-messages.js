require('dotenv').config({ path: '../.env' });
const fetch = require('node-fetch');

const URL_API_ID = process.env.APPSYNC_API_ID;
const REGION = process.env.AWS_REGION;
const API_KEY = process.env.APPSYNC_API_KEY;

const QUERY = `
query ListMessages($chatId: ID!) {
  listMessages(chatId: $chatId, limit: 50) {
    items {
      id
      role
      content
      createdAt
    }
  }
}`;

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
        query: QUERY,
        variables: {
          chatId: process.env.CHAT_ID,
        },
      }),
    });
    
    const data = await res.json();
    
    if (data.errors) {
      console.error('Erros:', data.errors);
      return;
    }
    
    console.log('Últimas mensagens (ordenadas por data):');
    const messages = data.data.listMessages.items.sort((a, b) => 
      new Date(a.createdAt) - new Date(b.createdAt)
    );
    
    messages.forEach((msg, i) => {
      console.log(`${i + 1}. [${msg.role.toUpperCase()}] ${msg.content}`);
      console.log(`   ID: ${msg.id} | ${msg.createdAt}`);
      console.log('');
    });
    
  } catch (err) {
    console.error('Erro:', err);
  }
})();
