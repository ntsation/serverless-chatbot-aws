import { util } from '@aws-appsync/utils';

export function request(ctx) {
  const messageId = util.autoId();
  const timestamp = util.time.nowISO8601();
  
  ctx.stash.messageId = messageId;
  ctx.stash.timestamp = timestamp;
  
  return {
    operation: 'PutItem',
    key: {
      chatId: util.dynamodb.toDynamoDB(ctx.arguments.chatId),
      sk: util.dynamodb.toDynamoDB(`${timestamp}#${messageId}`)
    },
    attributeValues: {
      id: util.dynamodb.toDynamoDB(messageId),
      role: util.dynamodb.toDynamoDB('assistant'),
      content: util.dynamodb.toDynamoDB(ctx.arguments.content),
      createdAt: util.dynamodb.toDynamoDB(timestamp)
    }
  };
}

export function response(ctx) {
  if (ctx.error) {
    return util.error(ctx.error.message, ctx.error.type);
  }
  
  return {
    id: ctx.stash.messageId,
    chatId: ctx.arguments.chatId,
    userId: null,
    role: 'assistant',
    content: ctx.arguments.content,
    createdAt: ctx.stash.timestamp
  };
}
