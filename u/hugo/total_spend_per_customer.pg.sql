select email, sum(total_price / 100) as spend
from orders, customers
where orders.customer_id = customers.id
group by email
order by spend desc