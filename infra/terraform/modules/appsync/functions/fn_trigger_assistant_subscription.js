import { util } from '@aws-appsync/utils';

export function request(ctx) {
  console.log('TriggerAssistantSubscription - ctx.stash:', JSON.stringify(ctx.stash));
  
  if (ctx.stash.assistantMessage) {
    const assistantMessage = ctx.stash.assistantMessage;
    console.log('TriggerAssistantSubscription - Triggerando subscription para:', JSON.stringify(assistantMessage));
    
    return {
      operation: 'Invoke',
      payload: {
        action: 'trigger_subscription',
        assistantMessage: assistantMessage
      }
    };
  }
  
  console.log('TriggerAssistantSubscription - Nenhuma mensagem do assistant, pulando...');
  
  return {
    operation: 'Invoke',
    payload: {
      action: 'skip'
    }
  };
}

export function response(ctx) {
  if (ctx.error) {
    console.log('TriggerAssistantSubscription - Error:', JSON.stringify(ctx.error));
    return util.error(ctx.error.message, ctx.error.type);
  }
  
  console.log('TriggerAssistantSubscription - ctx.result:', JSON.stringify(ctx.result));
  
  return ctx.stash.userMessage;
}
