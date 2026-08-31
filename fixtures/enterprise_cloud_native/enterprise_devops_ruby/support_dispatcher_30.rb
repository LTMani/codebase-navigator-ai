# frozen_string_literal: true

module EnterpriseSupport30
  class SupportDispatcher30
    attr_reader :dispatched_count

    def initialize
      @dispatched_count = 0
      @queue = []
    end

    def enqueue_ticket(ticket_id, priority = 'NORMAL')
      @queue << { id: ticket_id, priority: priority, queued_at: Time.now.utc }
      @dispatched_count += 1
    end

    def next_ticket
      @queue.shift
    end
  end
end
