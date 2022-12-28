# NBA Data Analyst: API y Web Scraping

## Objetivos:

- Evaluar el comportamiento del equipo seleccionado durante los partidos del año.
- Analizar las principales estadísticas del equipo hasta el momento para la temporada 2022-2023.
- Obtener un pronóstico para el próximo partido del equipo seleccionado.

## Contenidos:

- ETL que extrae y transforma datos de una API de datos de la NBA y guarde un informe de los puntos clave del equipo en cuestión en formato pdf:
  - Emplear los credenciales necesarios para obtener los datos requeridos de la API (para más información se proporciona un fichero config.txt en el repositorio).
  - Solicitar el nombre / ID del equipo del que se desea obtener la información.
  - Procesar el DataFrame para seleccionar los datos asociados a dicho equipo.
  - Solicitar la información de los jugadores del equipo mediante acceso a la API utilizada anteriormente (credenciales necesarios).
  - Generar PDF con la información procesada.
  
- ETL que obtiene datos usando técnicas de web scraping para ofrecer por pantalla la predicción para el próximo partido:
  - Extraer datos del html mediante el uso de la librería bs4 (Beautiful Soup) generando el árbol con los elementos.
  - Navegar por el árbol para obtener el pronóstico para el equipo.
