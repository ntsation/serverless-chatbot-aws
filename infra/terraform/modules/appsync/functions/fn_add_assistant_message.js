import { util } from '@aws-appsync/utils';

export function request(ctx) {
  const messageId = util.autoId();
  const timestamp = util.time.nowISO8601();
  
  return {
    operation: 'PutItem',
    key: {
      chatId: util.dynamodb.toDynamoDB(ctx.arguments.chatId),
      sk: util.dynamodb.toDynamoDB(`${timestamp}#${messageId}`)
    },
    attributeValues: {
      id: util.dynamodb.toDynamoDB(messageId),
      userId: util.dynamodb.toDynamoDB(ctx.arguments.userId),
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
    id: ctx.result.id,
    chatId: ctx.result.chatId,
    userId: ctx.result.userId,
    role: ctx.result.role,
    content: ctx.result.content,
    createdAt: ctx.result.createdAt
  };
}
