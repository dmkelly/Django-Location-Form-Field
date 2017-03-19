from django import forms

class LocationWidget(forms.widgets.Widget):
    """Forms widget to represent a location.
    
    Uses Google Maps API to represent a location on a map with a marker.
    """
    def __init__(self, *args, **kwargs):
        super(LocationWidget, self).__init__(*args, **kwargs)
    
    def render(self, name, value, attrs):
        if not value:
            lat, lon = (0,0,)
        else:
            lat, lon = value.split(',')

        html = []
        if attrs.get('help_text') is not None:
            html.append('<p>' + attrs['help_text'] + '</p>')
        html.append("""<div id="map" style="height:%(height)s;width:%(width)s;">
            <noscript>This page requires JavaScript.</noscript>
        </div>
        <input id="gmap_loc_%(name)s" type="hidden" name="%(name)s" value="%(value)s" />
        <script type="text/javascript">
            function initialize_map() {
                if(typeof(google) == 'undefined') {
                    document.getElementById('map').innerHTML = 'Google API not found';
                    return;
                }
                var options = {
                    center: new google.maps.LatLng(%(lat)s, %(lon)s),
                    zoom: 13,
                    mapTypeId: google.maps.MapTypeId.ROADMAP
                };
                %(name)s_map = new google.maps.Map(document.getElementById('map'),
                    options);
                var marker = new google.maps.Marker({
                    position: %(name)s_map.getCenter(),
                    draggable: true,
                    animation: google.maps.Animation.DROP,
                    map: %(name)s_map,
                    title: '%(marker_text)s'
                });
                google.maps.event.addListener(marker, 'position_changed', function() {
                    var valInput=document.getElementById('gmap_loc_%(name)s');
                    valInput.value = marker.getPosition().lat()+','+marker.getPosition().lng();
                });
                google.maps.event.addListener(%(name)s_map, 'resize', function() {
                    %(name)s_map.setCenter(%(name)s_map.getCenter());
                });
            }
            initialize_map();
        </script>
        """ % {'name': name, 'value':value,
               'height':self.attrs.get('height', '400px'),
               'width':self.attrs.get('width', '400px'),
               'lat': lat, 'lon': lon,
               'marker_text':self.attrs.get('marker_text', 'Drag the marker to the desired location')})
        return ''.join(html)

class LocationField(forms.Field):
    """This form field is used to obtain a latitude and longitude coordinate
    from a Google Map.
    """
    widget = LocationWidget
    
    def __init__(self, *args, **kwargs):
        super(LocationField, self).__init__(*args, **kwargs)
    
    def to_python(self, value):
        if not value:
            return None
        else:
            return {'latitude': self.__parse_latitude(value),
                        'longitude': self.__parse_longitude(value)}
    
    def __to_micro_coordinate(self, coord):
        """Only works on cleaned data."""
        if not coord:
            return None
        return int(float(coord) * 1000000)
    
    def validate(self, value):
        super(LocationField, self).validate(value)
        if type(value) is dict:
            self.__validate_as_dict(value)
        else:
            self.__validate_as_dict({'latitude':self.__parse_latitude(value),
                                   'longitude':self.__parse_longitude(value)})
            
    def __validate_as_dict(self, value):
        if not (value['latitude'] and value['longitude']):
            raise forms.ValidationError('Missing at least one coordinate')
        if value['latitude'] > 90.000000 or value['latitude'] < -90.000000:
            raise forms.ValidationError('Latitude out of range')
        if value['longitude'] > 180.000000 or value['longitude'] < -180.000000:
            raise forms.ValidationError('Longitude out of range')
    
    def __parse_latitude(self, value):
        return float(value.split(',')[0])
    
    def __parse_longitude(self, value):
        try:
            return float(value.split(',')[1])
        except IndexError:
            return None
