#! -*- coding: utf-8 -*-

import requests, base64, os, time

print("\n\n[*] INICIANDO PROJETO POKEDEX!!")

## DOWNLOAD IMAGEM
def imgDown(pokemonsize):
    print("\n\n[*] Iniciando download das imagens")
    for i in range(1,int(pokemonsize)):
        image_url="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/%s.png" % str(i)
        img_data = requests.get(image_url).content
        with open("./pokemonIMG/"+str(i)+'.png', 'wb') as handler:
            handler.write(img_data)
        print("[*] FINISH THE %sº IMAGE!" % str(i))

## DOWNLOAD JSON
def jsonDown(pokemonsize):
    print("\n\n[*] Baixando arquivos JSON")
    for i in range(1,int(pokemonsize)):
        os.system("curl -s -XGET \"https://pokeapi.co/api/v2/pokemon/%s\" > ./pokemonJSON/%s.json" %(str(i),str(i)))
        print("[*] FINISH THE %sº JSON FILE!" % str(i))

## REPLACE JSON BY BASE 64 IMAGES
def replaceIMG2BASE64(pokemonsize):
    print("\n\n[*] Copiando arquivos JSON")
    os.system("cp pokemonJSON/* pokemonJSON64")
    for i in range(1,int(pokemonsize)):
        with open("./pokemonIMG/"+str(i)+".png", "rb") as img_file:
            my_string = base64.b64encode(img_file.read())
        my_string = my_string.decode('ascii')
        url = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/%s.png" % str(i)
        os.system('sed -i "s,%s,%s,g" pokemonJSON64/%s.json' % (url,my_string,str(i)))
        print("[*] FINISH THE %sº JSON FILE!" % str(i))
        img_file.close()

## SENT JSON 2 ELASTICSEARCH
def sent2elastic(pokemonsize,ipElastic):
    print("\n\n[*] Enviando dados para Elasticsearhc")
    for i in range(1,int(pokemonsize)):

        index_list = open("pokemonJSON64/%s.json" % str(i)).read().split("{")

        habilidade_temp = ""
        tipo_temp = ""

        for j in index_list:
            if "ability" in j:
                if "name" in j:
                #     if not "types" in i:
                    habilidade = j.split('"')
                    habilidade = habilidade[3]
                    habilidade_temp = habilidade_temp + habilidade + ","
                    #print("\n\n"+habilidade)

        for k in index_list:
            if "type" in k:
                if "name" in k:
                    if not "types" in k:
                        typename = k.split('"')
                        typename = typename[3]
                        tipo_temp = tipo_temp + typename + ","
                        #print(typename)

        habilidade_temp = habilidade_temp.rstrip(",")
        tipo_temp = tipo_temp.rstrip(",")

        print("\n[*] SENT THE %sº POKEMON!" % str(i))
        print("[*] Habilidades: "+str(habilidade_temp))
        print("[*] Tipo: "+tipo_temp) 

        stringText = ",\"ability_name\":\"%s\",\"type_name\":\"%s\"}" % (habilidade_temp,tipo_temp)

        os.system("sed -i 's/.$//g' pokemonJSON64/%s.json" % str(i))
        os.system("echo '%s' >> pokemonJSON64/%s.json" % (stringText,str(i)))

        os.system("curl -s -H 'Content-Type: application/json' \
            -XPOST 'http://%s:9200/pokemon/_doc/' \
                --data-binary '@pokemonJSON64/%s.json'" % (ipElastic,str(i)))

def main():

    pokemonsize = input("Informe a quantidade de pokemons na API: ")
    pokemonsize = int(pokemonsize) + 1
    ipElastic = input("Informe o IP do Elasticsearch: ")

    os.system("rm -rf pokemonIMG pokemonJSON pokemonJSON64 && mkdir pokemonIMG pokemonJSON pokemonJSON64")
    
    imgDown(pokemonsize)
    
    jsonDown(pokemonsize)
    
    replaceIMG2BASE64(pokemonsize)

    ## ADD MYSELF
    os.system("curl -s -H 'Content-Type: application/json' \
            -XPOST '%s:9200/pokemon/_doc/' \
                --data-binary @joaoneto.json >> /dev/null" % (ipElastic))
    
    sent2elastic(pokemonsize,ipElastic)

if __name__ == "__main__":
    main()