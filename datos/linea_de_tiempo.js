const BANDAS={
regimen:{t:"Régimen",items:[[1854,1912,"restr","República restrictiva: voto cantado y fraude"],[1912,1930,"dem","Democracia ampliada (solo varones)"],[1930,1932,"facto","Golpe de Uriburu"],[1932,1943,"fraude","Fraude patriótico (Década Infame)"],[1943,1946,"facto","Golpe de 1943"],[1946,1955,"dem","Democracia (peronismo)"],[1955,1958,"facto","Revolución Libertadora"],[1958,1962,"proscr","Democracia con proscripción del peronismo"],[1962,1963,"facto","Derrocamiento de Frondizi; Guido bajo tutela militar"],[1963,1966,"proscr","Democracia con proscripción"],[1966,1973,"facto","Revolución Argentina"],[1973,1976,"dem","Democracia"],[1976,1983,"facto","Dictadura (Proceso)"],[1983,2027,"plena","Democracia plena"]]},
voto:{t:"Voto",items:[[1854,1912,"cant","Cantado, voluntario, solo varones"],[1912,1951,"sec","Secreto y obligatorio, solo varones (Ley Sáenz Peña)"],[1951,2013,"univ","Universal: votan las mujeres (Ley 13.010)"],[2013,2027,"joven","Universal desde los 16 años (Ley 26.774)"]]},
presidente:{t:"Elección del presidente",items:[[1854,1949,"col","Colegio electoral"],[1949,1955,"dir","Directa (Constitución de 1949)"],[1957,1966,"col","Colegio electoral"],[1972,1976,"bal","Directa con balotaje (Estatuto de 1972)"],[1983,1994,"col","Colegio electoral"],[1994,2027,"bal","Directa con balotaje (Reforma de 1994)"]]},
senado:{t:"Elección del Senado",items:[[1854,1949,"col","Por las legislaturas, 2 por provincia"],[1949,1955,"dir","Directa (Constitución de 1949)"],[1957,1966,"col","Por las legislaturas"],[1972,1976,"bal","Directa, 3 por provincia"],[1983,2001,"col","Por las legislaturas (3.º senador desde 1995)"],[2001,2027,"bal","Directa, 3 por provincia"]]},
instrumentos:{t:"Instrumentos",items:[[1854,2025,"bol","Boleta partidaria (desde 1912, lista de cada partido)"],[2025,2027,"bup","Boleta Única Papel (Ley 27.781)"]]},
paso:{t:"PASO",items:[[2011,2025,"paso","PASO vigentes (Ley 26.571)"],[2025,2026,"bol","2025: no se hicieron (suspensión por única vez, Ley 27.783)"],[2026,2027,"paso","Vigentes para 2027"]]}
};
const COL={restr:"#B8A88A",dem:"#74ACDF",facto:"#3B3B3B",fraude:"#C9822B",proscr:"#9FB6CC",plena:"#2F7FC1",cant:"#B8A88A",sec:"#9FB6CC",univ:"#74ACDF",joven:"#2F7FC1",col:"#B8A88A",dir:"#74ACDF",bal:"#2F7FC1",bol:"#D7E3EE",paso:"#F6B40E",bup:"#2F7FC1"};
const ELEC=[1854,1860,1862,1868,1874,1880,1886,1892,1898,1904,1910,1916,1922,1928,1931,1937,1946,1951,1958,1963,1973,1983,1989,1995,1999,2003,2007,2011,2015,2019,2023];
const LEG=[1912,1914,1918,1920,1924,1926,1930,1934,1936,1938,1940,1942,1948,1954,1960,1962,1965,1985,1987,1991,1993,1997,2001,2005,2009,2013,2017,2021,2025];
const HITOS=[
[1853,"Se sanciona la Constitución Nacional: presidente y senadores por elección indirecta."],
[1854,"Primera elección presidencial: Urquiza, por colegio electoral."],
[1857,"Primera ley electoral nacional: voto voluntario, cantado y por lista completa."],
[1904,"Ensayo de circunscripciones uninominales: Alfredo Palacios, primer diputado socialista de América."],
[1912,"Ley Sáenz Peña (8871): voto secreto, obligatorio y para todos los varones, con lista incompleta."],
[1916,"Primera presidencial con la nueva ley: gana Yrigoyen."],
[1930,"6 de septiembre: primer golpe de Estado, de Uriburu contra Yrigoyen."],
[1931,"Se anulan las elecciones bonaerenses ganadas por la UCR y se veta a Alvear; la UCR se abstiene. Empieza el fraude patriótico."],
[1943,"4 de junio: golpe militar."],
[1947,"Ley 13.010: voto femenino."],
[1949,"Nueva Constitución: elección directa de presidente y senadores, y reelección."],
[1951,"11 de noviembre: las mujeres votan por primera vez en una elección nacional."],
[1955,"Golpe contra Perón. Al año siguiente, el Decreto 4161 proscribe al peronismo."],
[1957,"Se deroga la Constitución de 1949 y vuelve el colegio electoral."],
[1962,"Las elecciones de marzo, con triunfos peronistas, se anulan; Frondizi es derrocado."],
[1966,"28 de junio: golpe contra Illia."],
[1972,"Estatuto Fundamental: elección directa con balotaje y tres senadores por provincia."],
[1973,"Marzo: gana Cámpora, Balbín no va al balotaje. Septiembre: Perón, ya sin proscripción."],
[1976,"24 de marzo: golpe de Estado."],
[1983,"30 de octubre: vuelve la democracia; gana Alfonsín."],
[1991,"Ley 24.012 de cupo femenino en las listas (se aplica desde 1993)."],
[1994,"Reforma constitucional: elección directa con balotaje, mandato de 4 años y tercer senador."],
[2001,"14 de octubre: primera elección directa de los tres senadores en todas las provincias."],
[2003,"Menem se retira antes del balotaje: Kirchner asume con el 22 % de los votos."],
[2009,"Ley 26.571: se crean las PASO."],
[2011,"Primeras PASO nacionales."],
[2012,"Ley 26.774: voto optativo desde los 16 años (desde 2013)."],
[2015,"Primer balotaje presidencial de la historia: gana Macri."],
[2017,"Ley 27.412 de paridad de género en las listas (desde 2019)."],
[2023,"Balotaje: gana Milei."],
[2024,"Ley 27.781: Boleta Única Papel."],
[2025,"Primera elección con Boleta Única Papel. Las PASO no se hicieron ese año: la Ley 27.783 las suspendió solo para 2025, y siguen vigentes para 2027."]
];
