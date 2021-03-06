from flask import Flask, render_template, url_for, redirect, g, request
import sqlite3

app=Flask(__name__)
db_location='var/test.db'

def get_db():
  db = getattr(g, 'db', None)
  if db is None:
    db=sqlite3.connect(db_location)
    g.db = db
    db.text_factory=str
  return db

@app.teardown_appcontext
def close_db_connection(exception):
  db = getattr(g, 'db', None)
  if db is not None:
    db.close()

def init_db():
  with app.app_context():
    db=get_db()
    with app.open_resource('schema.sql', mode='r') as f:
      db.cursor().executescript(f.read())
    db.commit()

@app.route("/")
@app.route("/browse")
def index():
  db=get_db()
  sql='SELECT * FROM Artists'
  queryArtists=db.cursor().execute(sql)
  sql='select * from Albums'
  queryAlbums=db.cursor().execute(sql)
  sql='select * from Tracks'
  queryTracks=db.cursor().execute(sql)
  artists=[]
  albums=[]
  tracks=[]
  for row in queryArtists:
    artists.append(row)
  for row in queryAlbums:
    albums.append(row)
  for row in queryTracks:
    tracks.append(row)
  db.close()
  return render_template('index.html',artists=artists,albums=albums,tracks=tracks)

@app.route("/browse/<artist>")
def browseArtist(artist):
  db=get_db()
  query="Select * from Albums,Artists where Artists.Name='"+artist+"'and Albums.ArtistID=Artists.ID"
  list=db.cursor().execute(query)
  artistsAlbums=[]
  for row in list:
    artistsAlbums.append(row)
  return render_template('browseArtist.html',artistsAlbums=artistsAlbums,artist = artist)

@app.route("/browse/<artist>/<album>")
def browseArtistsAlbum(artist,album):
  db=get_db()
  query="Select * from Tracks,Albums,Artists where Artists.Name='"+artist+"'and Albums.ArtistID=Artists.ID and Albums.Title='"+album+"' and Tracks.AlbumID=Albums.ID"
  list=db.cursor().execute(query)
  albumsTracks=[]
  for row in list:
    albumsTracks.append(row)
  return render_template('browseAlbum.html',albumsTracks=albumsTracks,album=album, artist=artist)

@app.route("/search")
def search():
  return render_template('search.html')

@app.route("/search/artist", methods=['GET','POST'])
def searchArtist():
  if request.method =="POST" :
    artist=request.form['artist']
    print artist
    return redirect(url_for('getArtists',artist=artist))
  else :
    return render_template('search.html')

@app.route("/search/artist/<artist>")
def getArtists(artist):
  db=get_db()
  query="Select * from Artists where Name='"+artist+"'"
  list=db.cursor().execute(query)
  artists=[]
  for row in list:
    artists.append(row)
  return render_template('searchArtist.html',artist=artist,artists=artists)

@app.route("/search/album", methods=['GET','POST'])
def searchAlbum():
  if request.method =="POST" :
    album=request.form['album']
    print album
    return redirect(url_for('getAlbums',album=album))
  else :
    return render_template('search.html')

@app.route("/search/album/<album>")
def getAlbums(album):
  db=get_db()
  query="Select Albums.Title, Artists.Name from Albums,Artists where Albums.Title='"+album+"' and Albums.ArtistID=Artists.ID"
  list=db.cursor().execute(query)
  albums=[]
  for row in list:
    albums.append(row)
  return render_template('searchAlbum.html',album=album,albums=albums)

@app.route("/search/track", methods=['GET','POST'])
def searchTrack():
  if request.method =="POST" :
    track=request.form['track']
    print track
    return redirect(url_for('getTracks',track=track))
  else :
    return render_template('search.html')

@app.route("/search/track/<track>")
def getTracks(track):
  db=get_db()
  query="Select Tracks.Name,Tracks.Length,Artists.Name,Albums.Title from Tracks,Albums,Artists where Tracks.Name='"+track+"' and Tracks.AlbumID=Albums.ID and Albums.ArtistID=Artists.ID"
  list=db.cursor().execute(query)
  tracks=[]
  for row in list:
    tracks.append(row)
  return render_template('searchTrack.html',track=track,tracks=tracks)

@app.route("/import")
def importing():
  return render_template('import.html')

@app.route("/import/artist/", methods=['POST','GET'])
def importingArtist():
  db=get_db()
  if request.method=="GET":
    return render_template('importArtist.html')
  else:
    print request.form
    name=request.form['name']
    bio=request.form['bio']
    image=request.files['image']
    print name
    print bio
    print image
    image.save('static/artistsPictures/'+name+'.png')
    query = 'insert into Artists(Name,Bio)values("'+name+'","'+bio+'")'
    db.cursor().execute(query)
    db.commit()
    return render_template('import.html')

@app.route("/import/album", methods=['POST','GET'])
def importingAlbum():
  db=get_db()
  if request.method=="GET":
    query="select Name from Artists"
    list=db.cursor().execute(query)
    artists=[]
    for row in list:
      artists.append(row[0])
    db.close()
    return render_template('importAlbum.html',artists=artists)
  else:
    print request.form
    title=request.form['title']
    artist=request.form['artist']
    image=request.files['image']
    print title
    print artist
    print image
    image.save('static/albumsPictures/'+title+'.png')
    query= "select ID from Artists where Name='"+artist+"'"
    artistID=db.cursor().execute(query)
    artistID=artistID.fetchone()
    artistID=str(artistID[0])
    print artistID[0]
    query= 'insert into Albums(Title,ArtistID)values("'+title+'","'+artistID[0]+'")'
    db.cursor().execute(query)
    db.commit()
    return render_template('import.html')

@app.route("/import/track", methods=['POST','GET'])
def importingTrack():
  db=get_db()
  if request.method=="GET":
    query="select Title from Albums"
    list=db.cursor().execute(query)
    albums=[]
    for row in list:
      albums.append(row[0])
    db.close()
    return render_template('importTrack.html',albums=albums)
  else:
    print request.form
    name=request.form['name']
    length=request.form['length']
    album=request.form['album']
    print name
    print length
    print album
    query="select ID from Albums where Title='"+album+"'"
    albumID=db.cursor().execute(query)
    albumID=albumID.fetchone()
    albumID=str(albumID[0])
    print albumID[0]
    query='insert into Tracks(Name,Length,AlbumID)values("'+name+'","'+length+'","'+albumID[0]+'")'
    db.cursor().execute(query)
    db.commit()
    return render_template('import.html')

@app.errorhandler(404)
def page_not_found(error):
  return "The page you're trying to reach doesn't exist man.", 404

if __name__ == "__main__":
  app.run(host='0.0.0.0',debug=True)
