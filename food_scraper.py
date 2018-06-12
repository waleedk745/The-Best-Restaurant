from bs4 import BeautifulSoup
import requests
import re
from psycopg2 import sql
import psycopg2
import sys
from googleplaces import GooglePlaces,types

from osgeo import ogr
from math import cos,sin,acos


class best_restaurant:
    'Class for all the functions used for find the best reastaurant'
    def __init__(self,city,location,dish,min_range,max_range):
        
        self.city=city
        self.dish=dish
        self.min_range=min_range
        self.max_range=max_range
        self.location=location
    def all_restaurants(self):
        url='https://www.foodpanda.pk/city/'+self.city
        print(url)
        r=requests.get(url)
        data=r.text
        soup=BeautifulSoup(data,'html.parser')
        name= soup.find_all("span", {"class": "name fn"})
        n= list(name)
        restaurants=[re.sub(r'<.+?>',r'',str(a)) for a in n]  
        return restaurants
    
    def restaurant_urls(self,restaurants):
        url='https://www.foodpanda.pk/city/'+self.city
        r=requests.get(url)
        data=r.text
        soup=BeautifulSoup(data,'html.parser')
        ur=[]
        for tag in soup.findAll('a', href=True):
            ur.append(tag['href'])
        a="/restaurant"
        b="/chain"
        final=[]
        for e in ur:
            if a in e or b in e:
                final.append(e)
            else:
                pass
        uru=[]
        a="https"
        for e in final:
            if a not in e :
                uru.append(e)
        urls=dict()
        for i in range (len(restaurants)):
            urls.update({restaurants[i]:uru[i]})  
        return urls
    def dish_per_res(self,urls,restaurants):
        dish_per_restaurant=dict()
        for e in range(len(urls)):
            a=restaurants[e]
            c=urls[a]
            url='https://www.foodpanda.pk'
            url=url+c
            r=requests.get(url)
            data=r.text
            soup=BeautifulSoup(data,'html.parser')
            name=soup.find_all("div",{"class":"dish-card h-product menu__item"})
            n=list(name)
            d=[re.sub(r'<.+?>',r'',str(a))for a in n]
            restaurant_name=restaurants[e]
            p=[]
            for i in range(len(d)):
                b=[]
                dish=d[i]
                a=(" ".join(dish.split()))
                k=a.split()
                k.remove("Add")
                for e in k:
                    if "Rs" in e :
                        b.append(e)
                del(k[-1])     
                string = ' '.join(k)
                b.append(string)
                p.append(b)
            dish_per_restaurant.update({restaurant_name:p})  
        return dish_per_restaurant
    def database_writer(self,restaurants,dish_per_restaurant):
         conn = psycopg2.connect(database = "Students", user = "postgres", password = "1234", host = "localhost", port = "5432")
         print ("Opened database successfully")   
         cur = conn.cursor() 
         table="restaurants"   
         for i in range(len(restaurants)):
             val=restaurants[i]
             dishp=dish_per_restaurant[val]
             
             id_res=i+1
             for e in range(len(dishp)):
                 c=dishp[e]
                 price=list(c[0])
                 price.remove("R")
                 price.remove("s")
                 for g in price:
                     if g in [","]:
                         price.remove(",")
                     else:
                         pass
        
         price=''.join(price)
         price=int(price)
         dish=c[1]
         cur.execute(sql.SQL("insert into {} values (%s, %s, %s,%s)").format(sql.Identifier(table)),[id_res, val, dish,price])
         conn.commit()                    
    def data_extractor(self,dish,min_range,max_range):
        dish=self.dish
        min_range=self.min_range
        max_range=self.max_range
        best_restaurants=[]
        best=[]
        try:
            conn = psycopg2.connect(database = "Students", user = "postgres", password = "1234", host = "localhost", port = "5432")
           
        except:
            print("Cannot connect to the database")
            sys.exit(1)
        cur = conn.cursor() 
        query="SELECT Restaurant FROM restaurants WHERE dish ilike"+" '%"+str(dish)+"%'"+" " +"and"+" "+"price Between"+" "+str(min_range)+" "+"and "+" "+str(max_range)
        cur.execute(query)
        best_rest = list(set(cur.fetchall()))
        for i in range (len(best_rest)):
            best_restaurants.append(str(best_rest[i][0]))
        for e in best_restaurants:
            e.replace("&amp","")
            e.replace(",","")
            e.replace("  ","")
            best.append(e)
        return best
    def best_retaurants_location(self,best_restaurants,user_coords):
        best_restaurant_loc=[]
        api_key='AIzaSyDgm1wATqS6zUAIB5BEyVGmfAo0uYdjO6o'
        loc=user_coords
        google_places = GooglePlaces(api_key)
        for restaurant in best_restaurants:
            word=restaurant
            query_result = google_places.nearby_search(
                    lat_lng=loc , keyword=word,
                    radius=20000,types=[types.TYPE_FOOD])
            for place in query_result.places:
                best_restaurant_loc.append(place.geo_location)
                best_restaurant_loc.append(place.name)
        return best_restaurant_loc
    def user_location(self):
        city=self.city
        location=self.location
        location=location.replace(" ","+")
        api_key='AIzaSyCLpZPtZUu-h9NBuHVd9HgkC6EHuP64Ud4'
        google='https://maps.googleapis.com/maps/api/geocode/json?address='
        url=google+location+','+city+'&key='+api_key
        search=requests.get(url)
        search_json=search.json()
        user_coords=search_json['results'][0]['geometry']['location']
        return user_coords    
    def directions_finder(self,user_coords,best_restaurant):
        api_key='AIzaSyCLpZPtZUu-h9NBuHVd9HgkC6EHuP64Ud4'
        google='https://maps.googleapis.com/maps/api/directions/json?origin='
        url=google+str(user_coords['lat'])+','+str(user_coords['lng'])+'&destination='+str(best_restaurant[1][0])+","+str(best_restaurant[1][1])+'&key='+api_key
        search=requests.get(url)
        search_json=search.json()
        return search_json["routes"][0]["overview_polyline"]["points"]  
    def decode(self,point_str):
    
             
    
        coord_chunks = [[]]
        for char in point_str:
         
        
            value = ord(char) - 63
         
        
            split_after = not (value & 0x20)         
            value &= 0x1F
         
            coord_chunks[-1].append(value)
         
            if split_after:
                    coord_chunks.append([])
         
        del coord_chunks[-1]
     
        coords = []
     
        for coord_chunk in coord_chunks:
            coord = 0
         
            for i, chunk in enumerate(coord_chunk):                    
                coord |= chunk << (i * 5) #there is a 1 on the right if the coord is negative if coord & 0x1: coord = ~coord #invert coord >>= 1
            coord /= 100000.0
                     
            coords.append(coord)
     
    # convert the 1 dimensional list to a 2 dimensional list and offsets to 
    # actual values
        points = []
        prev_x = 0
        prev_y = 0
        for i in range(0, len(coords) - 1, 2):
            if coords[i] == 0 and coords[i + 1] == 0:
                continue
         
            prev_x += coords[i + 1]
            prev_y += coords[i]
            # a round to 6 digits ensures that the floats are the same as when 
            # they were encoded
            points.append((round(prev_x, 6), round(prev_y, 6)))
     
        return points 
    def shapefile_creator_multiline(self,points):
        c=[ points[i:i+2] for i in range(0, len(points), 2) ]
        multiline = ogr.Geometry(ogr.wkbMultiLineString)
        line1 = ogr.Geometry(ogr.wkbLineString)
    
        for i in range(len(c)):   
            g=c[i]
            if (len(g)==2):
                
                x1=g[0][0]
                y1=g[0][1]
                x2=g[1][0]
                y2=g[1][1]
            
                line1.AddPoint(y1, x1)
                line1.AddPoint(y2, x2)
                multiline.AddGeometry(line1)
            else:
                pass
        wkt_path=multiline.ExportToWkt() 
        
           
        return wkt_path
    def distance_finder(self,rest,coords):
        sequenced=[ rest[i:i+2] for i in range(0, len(rest), 2) ]
        slat=coords["lat"]
        slon=coords["lng"]
        restaurant_distance=[]
        selected_restaurants=[]
        rest_coords=[]
        for i in range(len(sequenced)):
            sets=[]
            elat=float(sequenced[i][0]["lat"])
            elon=float(sequenced[i][0]["lng"])
            dist = 6371.01 * acos(sin(slat)*sin(elat) + cos(slat)*cos(elat)*cos(slon - elon))
            restaurant_distance.append(dist)
            selected_restaurants.append(sequenced[i][1])
            sets.append(elat)
            sets.append(elon)
            rest_coords.append(sets)
        minimum_distance=min(restaurant_distance)
        minimum_distance_index=restaurant_distance.index(minimum_distance) 
        final_restaurant=selected_restaurants[minimum_distance_index]
        final_restaurant_coords=rest_coords[minimum_distance_index]
        return final_restaurant,final_restaurant_coords


    def user_wkt(self,user_coords):
        x=user_coords["lng"]
        y=user_coords["lat"]
        point = ogr.Geometry(ogr.wkbPoint)
        point.AddPoint(x,y)
        user_point=point.ExportToWkt()
        return user_point
    def restaurant_wkt(self,final_restaurant):
        x=final_restaurant[1][1]
        y=final_restaurant[1][0]
        point = ogr.Geometry(ogr.wkbPoint)
        point.AddPoint(x,y)
        restaurant_point=point.ExportToWkt()
        return restaurant_point
    def shortner(self):
        conn = psycopg2.connect(database = "Students", user = "postgres", password = "1234", host = "localhost", port = "5432")
        cur = conn.cursor() 
        cur.execute("select * from information_schema.tables where table_name=%s", ('restaurants',))
        a=bool(cur.rowcount)
        return a
