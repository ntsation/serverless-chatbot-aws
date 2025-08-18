import { util } from '@aws-appsync/utils';

export function request(ctx) {
  // Se for parte de um pipeline, use o resultado da função anterior
  const userMessage = ctx.prev.result;
  
  return {
    operation: 'Invoke',
    payload: {
      arguments: {
        chatId: ctx.arguments.chatId || userMessage.chatId,
        content: ctx.arguments.content || userMessage.content
      },
      identity: {
        sub: ctx.identity.sub,
        username: ctx.identity.username
      },
      source: ctx.source,
      userMessage: userMessage
    }
  };
}

export function response(ctx) {
  if (ctx.error) {
    return util.error(ctx.error.message, ctx.error.type);
  }
  return ctx.result;
}
