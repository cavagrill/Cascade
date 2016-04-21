# Cascade

Cascade was born from the idea that views can be built on top of views. It is quite common, as you will see with the demo data to have views built on top of views. 

## Create_silly_data.py
The purpose of this file is to create some fake date and load it into a database using cavaconn, a connection tool. You may choose to
download the files provided here and upload them yourself.

## album_summary
```select album,avg(duration) as avg_duration,max(duration) as longest_song,sum(case when explicit is False then 0 else 1 end),
        max(track_number) as record_count
        from tracks
        group by 1;```

## artist_summary
```create view artist_summary as
select a.id,a.name,a.followers,max(marketsize) as largest_market,count(distinct al.id) as albums,avg(longest_song) as
avg_longest_song
from artists a
inner join
albums al
on a.id=al.artists
inner join
album_summary als
on al.id=als.album
group by 1,2,3;```

##  example

### using python
Be sure to update rebirth.json
``` python cascade.py ```

### using CLI

``` python cascade.py album_summary view "select album,avg(duration) as avg_duration,min(duration) as
shortest_song,max(duration) as longest_song,sum(case when explicit is False then 0 else 1 end), max(track_number) as
record_count from tracks group by 1;" test_tables ```

