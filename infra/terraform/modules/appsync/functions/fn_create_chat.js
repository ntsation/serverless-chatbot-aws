import { util } from '@aws-appsync/utils';

export function request(ctx) {
  const chatId = util.autoId();
  
  return {
    operation: 'PutItem',
    key: {
      id: util.dynamodb.toDynamoDB(chatId)
    },
    attributeValues: {
      id: util.dynamodb.toDynamoDB(chatId),
      userId: util.dynamodb.toDynamoDB(ctx.identity.sub),
      title: util.dynamodb.toDynamoDB(ctx.arguments.title),
      createdAt: util.dynamodb.toDynamoDB(util.time.nowISO8601())
    }
  };
}

export function response(ctx) {
  if (ctx.error) {
    return util.error(ctx.error.message, ctx.error.type);
  }
  return ctx.result;
}
