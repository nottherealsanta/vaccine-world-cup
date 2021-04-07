import pandas as pd
import numpy as np

# CONFIG

HEIGHT = 800
WIDTH = 200

dont_draw_list = ['China']
draw_text_finish_line_list = ["World"]

location_list = ['India', 'United States','European Union', 'Africa','South America', 'China','World']
color_list = ['#FF9933', '#2D89FF' ,'#0055FF','#00c918','#f8ff33',"#DE2910",'#cccccc']

font_str = '''font-family: 'Open Sans', sans-serif;'''

# vaccination data
vac_df = pd.read_csv('/Users/santa/Projects/vaccine-world-cup/data/data.csv').drop(0)
vac_df.total_vaccinations = pd.to_numeric(vac_df.total_vaccinations)
vac_df.date = pd.to_datetime(vac_df.date)

# population data
pop_df = pd.read_csv('/Users/santa/Projects/vaccine-world-cup/data/pop_data.csv')

# combine df
df = vac_df[['location','date','iso_code','people_vaccinated','people_vaccinated_per_hundred']].merge(pop_df[['iso_code','population']], on=['iso_code'], how='inner')

# Function
def get_graph_for_location( location, color='black', hor_scale=1.2, ver_scale=1): 

    # graphs

    format_df = df[df.location=='World'].sort_values('date').reset_index()['date'].to_frame()
    location_df = df[df.location==location].set_index('date').people_vaccinated.fillna(method='bfill').to_frame().reset_index()
    m_df = format_df.merge(location_df, on=['date'], how='left').fillna(0)

    vacc_list = [ HEIGHT-(i * ver_scale) for i in ((m_df.people_vaccinated/10000000).values.tolist())]
    ran_list = [ (i * hor_scale) for i in  list(range(0, len(vacc_list)))]
    path_string = ""
    for i,j in zip(ran_list, vacc_list) :
        path_string += "L "
        path_string += (str(i)+" ")
        path_string += (str(j)+" ")

    d_string_area = 'M 0 '+str(HEIGHT)+ path_string + 'L '+str(ran_list[-1])+' '+str(HEIGHT)+' z'
    d_string_line = 'M 0 '+str(HEIGHT)+ path_string + ' '
    
    area_svg = "<path fill=\"{1}\" stroke-width=0.5 opacity=0.1 d=\"{0}\"/>".format(d_string_area, color)
    line_svg = "<path fill=\"none\" stroke-width=0.5 stroke=\"{1}\" d=\"{0}\"/>".format(d_string_line, color)

    loc_x = ran_list[-1]*2
    loc_y = vacc_list[-1]

    # circle 
    circle_svg = '''
        <circle 
            cx="{x}" 
            cy="{y}" 
            r="1" stroke="{color}" 
            stroke-width="0.5" 
            fill="none" 
            transform="scale (0.5,1)"/>
        <circle 
            cx="{x}" 
            cy="{y}" 
            r="0.5" stroke="none" 
            stroke-width="0.5" 
            fill="{color}" 
            transform="scale (0.5,1)"/>
    '''.format(x=loc_x , y=loc_y, color=color)

    # finish line
    finish_line_loc = HEIGHT - df[df.location==location].population.values[0]/10000000
    finish_line_svg = '''
    <path 
        fill="none" stroke="{color}" 
        stroke-width="0.25" 
        stroke-dasharray="1,1" 
        d="M0 {value} l200 0">
    </path>'''.format( 
        value =  finish_line_loc,
        color = color)

    # draw text on finish line : "World"
    if location in draw_text_finish_line_list:
        finish_line_svg +='''
        <text x="375" y="{value}" 
            style="{font_str}"
            text-anchor="end" 
            font-size="4" 
            transform="scale (0.5,1)" 
            fill="white">
            World Finish Line
        </text>'''.format(
            value=finish_line_loc-1,
            font_str=font_str)

    # don't draw graphs for china
    if location in dont_draw_list:
        ret_string = "\t {}".format(finish_line_svg)
    else :
        # ret_string =  "\t {0}\n\t {1}\n\t {2}\n\t {3}".format(area_svg, line_svg,text_svg, finish_line_svg)
        ret_string = "\n\t".join([area_svg, line_svg, finish_line_svg, circle_svg])

    return ret_string, loc_x, loc_y

def get_text_for_location(location, color, loc_x, loc_y):

    text_svg = '''
    <text 
        x="{x}" y="{y}" 
        style="{font_str}"
        text-anchor="start" 
        font-size="3.5" 
        transform="scale (0.5,1)" 
        fill="{color}">
        &nbsp;{location}
            <tspan
                style="{font_str}"
                text-anchor="start" 
                font-size="2.5" 
                transform="scale (0.5,1)" 
                fill="#eee">
                {percent_vac:.1f}%
            </tspan>
    </text>'''.format(
        x=loc_x,
        y=loc_y,
        location=location,
        color=color,
        percent_vac=df[df.location==location].people_vaccinated_per_hundred.max(),
        font_str=font_str
    )

    return text_svg

def group_location (locations = [], colors = []):

    ret_string = ""
    text_loc_df = pd.DataFrame(columns=['location','x','y'])
    
    #graphs
    for l, c in zip(locations, colors):
        r, x, y = (get_graph_for_location(location=l, color=c))
        ret_string += r
        text_loc_df = text_loc_df.append({'location':l,'x':x, 'y':y}, ignore_index=True)

    # adjusting texts not to overlap
    tolerance = 4
    text_loc_df = text_loc_df[~text_loc_df.location.isin(dont_draw_list)].sort_values('y',ascending=False).reset_index(drop=True)
    for index,row  in text_loc_df.iloc[1:].iterrows():
        prow_y = text_loc_df.iloc[index-1].y
        if prow_y-row.y < tolerance:
            text_loc_df.at[index,'y'] = prow_y-tolerance
    
    #texts
    for l,c in zip(locations, colors):
        r = get_text_for_location(
            l, c, 
            text_loc_df[text_loc_df.location==l].x + 5, 
            text_loc_df[text_loc_df.location==l].y )
        ret_string+= r

    return ret_string

def grid_pattern():

    ret_string = '''
        <defs>
            <pattern 
                id="pattern1" 
                patternUnits="userSpaceOnUse" 
                x="0" y="0" width="10" height="10" 
                viewBox="0 0 4 4">
                <path 
                    d="M 0 0 L 0 4 L 4 4 L 4 0 Z" 
                    fill="none" 
                    stroke-width="0.05" 
                    stroke="#575757"></path>
            </pattern>
  
        </defs>
        <g>
            <rect x="0" y="0" 
                  width="100%" 
                  height="100%" 
                  fill="url(#pattern1)" />
        </g>
    '''

    grid_tick_y = ""
    for i in range(5, 80,5):
        grid_tick_y += ''' <text x="15" y="{y}" >{pop:.1f}B</text>'''.format(pop=i/10, y= 800-(i*10))
    grid_tick_y = '''
    <g fill="#aaa" style="{font_str}"text-anchor="start" font-size="2.5" transform="scale (0.5,1)" >
        {tick}
    </g>
    '''.format(tick=grid_tick_y, font_str=font_str)

    return ret_string + grid_tick_y

def background():
    return '''
        <defs xmlns="http://www.w3.org/2000/svg">
					<linearGradient xmlns="http://www.w3.org/2000/svg" id="gradient-fill" x1="0" y1="0" x2="800" y2="0" gradientUnits="userSpaceOnUse">				
							<stop offset="0" stop-color="#060d20"/>
                            <stop offset="0.14285714285714285" stop-color="#091228"/>
                            <stop offset="0.2857142857142857" stop-color="#091630"/>
                            <stop offset="0.42857142857142855" stop-color="#091a38"/>
                            <stop offset="0.5714285714285714" stop-color="#0a1d40"/>
                            <stop offset="0.7142857142857142" stop-color="#0b2149"/>
                            <stop offset="0.8571428571428571" stop-color="#0c2451"/>
                            <stop offset="1" stop-color="#0e285a"/>
					</linearGradient>
				</defs>

    <rect fill="url(#gradient-fill)" width="200" height="800"/>
    '''

def get_title_info():
    return '''
        <div 
            style="
                height: 375%;width: 100%;
                background-color:rgba(0, 0, 0, 0.01);
                position:relative;
                top:25%;
                text-align: center;">
        <h1 
            style="
                color:white;
                text-shadow: 3px 3px black;
                font-size: 100px;  
                font-family: 'Raleway', sans-serif;"> 
            Vaccine World Cup
        
        <sub 
            style="
                color:#ff4444;
                text-shadow: 0px 0px black;
                font-size: 20px;  
                font-family: 'Open Sans', sans-serif; "> 
            COVID-19
        </sub></h1>

        <p
        style="
                color:#ffffff;
                text-shadow: 0px 0px black;
                font-size: 15px;  
                font-family: 'Open Sans', sans-serif; "> 
            powered by
        </p>
        <a target="_blank" href="https://ourworldindata.org/explorers/coronavirus-data-explorer?zoomToSelection=true&time=40..latest&pickerSort=desc&pickerMetric=total_vaccinations_per_hundred&Metric=People+vaccinated&Interval=Cumulative&Relative+to+Population=false&Align+outbreaks=false&country=OWID_WRL~IND~Africa~European+Union~USA~South+America">
        <img 
        src="data/OurWorldinData-logo.png" 
        height="2%">
        <p
        style="
                color:#ffffff;
                text-shadow: 0px 0px black;
                font-size: 10px;
                margin-top : 0px;  
                font-family: 'Open Sans', sans-serif; "> 
            click to explore more
        </p>

        <p
        style="
                color:#ffffff;
                text-shadow: 0px 0px black;
                font-size: 18px;
                position: relative;
                margin-top : 20%;  
                font-family: 'Raleway', sans-serif; "> 
                
        </p>
        <img 
        src="data/scroll-down.png" 
        height="0.5%">
        </a>
        

        <div
            style="
                height: 3%;width: 20%; right:0; bottom:0;
                background-color:rgba(0, 0, 0, 0.1);
                position:fixed;
                text-align: right;">
            <p
            style="
                    color:#ffffff;
                    text-shadow: 0px 0px black;
                    font-size: 15px;
                    bottom : 0px;
                    font-family: 'Open Sans', sans-serif; "> 
                last updated : 5th April 2021
            </p>
        </div>

        </div>
        '''.format()

# main html string

html_string = '''
<html style="width:100%;height:100%;">
<head>
    <title>Vaccine World Cup</title>
    <link rel="preconnect" href="https://fonts.gstatic.com">
    <link href="https://fonts.googleapis.com/css2?family=Open+Sans:wght@500&family=Raleway:wght@400&display=swap" rel="stylesheet">
    <!-- Global site tag (gtag.js) - Google Analytics -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-NW9QW6H8S4"></script>
    <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());

    gtag('config', 'G-NW9QW6H8S4');
    </script>
</head>
<body style="width:100%;height:100%;margin:0;">
<div style="height: 400%; width: 100%; border:2px solid #000;  position: absolute;" >
    <svg height="100%" width="100%" viewBox="0 0 200 800" position="absolute" preserveAspectRatio="none" >
        {background}
        {grid_pattern}
        {group_location}
    </svg>
</div>
{title_info}
</body>
</html>
'''.format(

    group_location = group_location(
    locations=location_list,
    colors=color_list,
    ),

    grid_pattern = grid_pattern(),

    background = background(),

    title_info = get_title_info()

    )


f = open('/Users/santa/Projects/vaccine-world-cup/index.html','w')
f.write(html_string)
f.close()

