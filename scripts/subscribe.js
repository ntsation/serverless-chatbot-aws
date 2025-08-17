const WebSocket = require('ws');
const crypto = require('crypto');

const API_ID = '';
const REGION = '';
const API_KEY = '';

const SUBSCRIPTION = `
subscription OnMessageSent($chatId: ID!) {
  onMessageSent(chatId: $chatId) {
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
  chatId: '',
};

const headers = {
  host: `${API_ID}.appsync-api.${REGION}.amazonaws.com`,
  'x-api-key': API_KEY,
};

const headerB64 = Buffer.from(JSON.stringify(headers)).toString('base64');
const payloadB64 = Buffer.from(JSON.stringify({})).toString('base64');

const wsUrl = `wss://${API_ID}.appsync-realtime-api.${REGION}.amazonaws.com/graphql?header=${headerB64}&payload=${payloadB64}`;

const ws = new WebSocket(wsUrl, 'graphql-ws');

ws.on('open', () => {
  console.log('>> Conexão aberta');

  ws.send(JSON.stringify({ type: 'connection_init' }));
  console.log('>> connection_init enviado');
});

ws.on('message', (data) => {
  const msg = JSON.parse(data);
  
  if (msg.type === 'data' && msg.payload && msg.payload.data && msg.payload.data.onMessageSent) {
    const message = msg.payload.data.onMessageSent;
    console.log('Nova mensagem recebida:');
    console.log(`ID: ${message.id}`);
    console.log(`Chat ID: ${message.chatId}`);
    console.log(`Usuário: ${message.userId}`);
    console.log(`Role: ${message.role}`);
    console.log(`Conteúdo: ${message.content}`);
    console.log(`Data: ${message.createdAt}`);
    console.log('---');
  } else {
    console.log('<<', JSON.stringify(msg, null, 2));
  }

  if (msg.type === 'connection_ack') {
    const id = crypto.randomBytes(4).toString('hex');
    const startMsg = {
      id,
      type: 'start',
      payload: {
        data: JSON.stringify({
          query: SUBSCRIPTION,
          variables: VARIABLES,
        }),
        extensions: {
          authorization: headers,
        },
      },
    };
    ws.send(JSON.stringify(startMsg));
    console.log('>> subscription enviada');
  }
});

ws.on('close', (code, reason) => {
  console.log('Conexão fechada:', code, reason.toString());
});

ws.on('error', (err) => {
  console.error('Erro:', err);
});
