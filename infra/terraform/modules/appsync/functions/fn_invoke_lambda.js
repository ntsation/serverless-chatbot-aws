import { util } from '@aws-appsync/utils';

export function request(ctx) {
  const userMessage = ctx.prev.result;
  
  ctx.stash.userMessage = userMessage;
  
  return {
    operation: 'Invoke',
    payload: {
      arguments: {
        chatId: ctx.arguments.chatId || userMessage.chatId,
        content: ctx.arguments.content || userMessage.content
      },
      identity: {
        sub: ctx.identity?.sub || 'api-key-user',
        username: ctx.identity?.username || 'api-key-user'
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
  return ctx.stash.userMessage;
}
