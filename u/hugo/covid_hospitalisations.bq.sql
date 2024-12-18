-- @year (integer) = 2022
select country_name, sum(new_hospitalized_patients) as total_hospitalized 
from demo.covid19 
where EXTRACT(isoyear from date) = @year
group by country_name
order by total_hospitalized desc
