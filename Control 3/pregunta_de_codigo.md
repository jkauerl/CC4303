# Preguntas de Codigos

## 1.- [Forwarding] 
Al intentar enviar  el mensaje 127.0.0.1;8885;13;hola router al R1, su router se cae. ¿Por qué ocurre esto?¿Qué ocurriría con el router default para el caso Round Robin? ¿Queremos este comportamiento?¿Como lo podemos cambiar?

La razón por la cual ocurre esto, es porque el mensaje que se está enviando ocupa ";" como separador, mientras que tal como se muestra en el código, este ocupa "," como separador (tal cual como se ocupa en las otras actividades de este control). Por lo tanto el router default solamente 

## 2.- [Fragmentación]&nbsp;  
Al correr en consola:&nbsp;  
nc -u 127.0.0.1 8881 << EOF&nbsp;  
127.0.0.1,8881,010,00000347,0000000,00000008,0,hola&nbsp;  
EOF&nbsp;  
Su implementación se cae. ¿Por qué ocurre esto?&nbsp;  

La razón por la cual ocurre esto es porque no se está manejando correctamente el caso cuando se tiene un mensaje de largo 1. Esto porque la función reassemble_IP_packet, al manejar el caso donde se tiene un largo de 1, retorna una lista de lista con el mensaje IP, y también su mensaje asociado. Además como después en el router se invoca la función parse_packet, se tiene que retornar el mensaje IP completo para que lo parsee y se obtenga el mensaje a retornar.

## 3- [BGP] 
Como menciona no se implementó la lectura de las nuevas tablas de rutas.¿Cómo modificaría su código? Explique el nuevo formato de las tablas de rutas para BGP.

Para que funcione las nuevas tablas de rutas, se tienen que hacer modificaciones al código implementado en la actividad. La función que se tiene que modificar corresponde a check_routers, pues cuando se lee la linea de la tabla de rutas, solamente se tiene que checkear que el primer router en la tabla corresponde al que se le tiene que enviar el mensaje, y si es así, entonces se envía el mensaje al router que se encuentra antes de si mismo en los routers de esa ruta.

La razón por la cual funciona esto es porque como cada router tiene almacenado la ruta a todos los routers, solamente se chequea la ruta a seguir, y que todos los demas routers también lo tendrán.