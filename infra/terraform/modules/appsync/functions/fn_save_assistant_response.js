import { util } from '@aws-appsync/utils';

export function request(ctx) {
  console.log('SaveAssistantResponse - ctx.prev.result:', JSON.stringify(ctx.prev.result));
  
  if (ctx.prev.result && ctx.prev.result.assistantMessage) {
    console.log('SaveAssistantResponse - Mensagem do assistant encontrada, adicionando ao stash');
    ctx.stash.assistantMessage = ctx.prev.result.assistantMessage;
  } else {
    console.log('SaveAssistantResponse - Nenhuma mensagem do assistant encontrada');
  }
  
  return {
    operation: 'GetItem',
    key: {
      chatId: util.dynamodb.toDynamoDB('__dummy__'),
      sk: util.dynamodb.toDynamoDB('__dummy__')
    }
  };
}

export function response(ctx) {
  if (ctx.error) {
    console.log('SaveAssistantResponse - Error:', JSON.stringify(ctx.error));
    return util.error(ctx.error.message, ctx.error.type);
  }
  
  console.log('SaveAssistantResponse - ctx.result:', JSON.stringify(ctx.result));
  
  console.log('SaveAssistantResponse - Retornando mensagem do usuário do stash');
  return ctx.stash.userMessage;
}
