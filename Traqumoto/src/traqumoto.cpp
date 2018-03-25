/* Copyright
Copyright Manuel MATILDE, contact: mtld.manu@gmail.com,
Copyright Maxime LEIBER, contact: leibermaxime@gmail.com,
Copyright Antoine SOUSTELLE, contact: antoine.soustelle@wanadoo.fr.
Programme crée le 6 mars 2017.*/

/* Licence
Ce logiciel est régi par la licence CeCILL soumise au droit français et
respectant les principes de diffusion des logiciels libres. Vous pouvez
utiliser, modifier et/ou redistribuer ce programme sous les conditions
de la licence CeCILL telle que diffusée par le CEA, le CNRS et l'INRIA 
sur le site "http://www.cecill.info".*/

/* Logiciel
Ce fichier fait parti du logiciel Traqu'moto, servant à la détection
des deux roues motorisés sur autoroute. Il a été réalisé sur commande
du Cerema.*/

/* Description du ficher
Ce fichier se lance via l'executable. Le `main` initialise Lua, charge
les librairies Lua, y ajoute la fonction getFile et execute le fichier
traqumoto.lua */

#include <stdio.h>
#include <stdlib.h>
#include <string>

using namespace std;

extern "C" {	/* charge les librairies Lua */
	#include "../Applications/torch/exe/luajit-rocks/luajit-2.1/src/lua.h"
	#include "../Applications/torch/exe/luajit-rocks/luajit-2.1/src/lualib.h"
	#include "../Applications/torch/exe/luajit-rocks/luajit-2.1/src/lauxlib.h"
}

/* interpreteur */
lua_State* L;

/* La fonction getFile permet de recupérer la vidéo à traiter */
static int getFile(lua_State *L)
{

	FILE *in;
	if (!(in = popen("bash -c 'zenity  --title=\"Select an image or a video\" --file-selection' &> /dev/null","r")))
	{
		fprintf(stderr, "[TRM] Couldn't use zenity to get a file from the user.\n");
    	abort();
	}

	char buff[512];
	string selectFile = "";
	while (fgets(buff, sizeof(buff), in) != NULL)
	{
		selectFile += buff;
	}
	pclose(in);

	/* push the return */
	lua_pushstring(L, selectFile.c_str());

	/* return the number of results */
	return 1;
}

int main ( int argc, char *argv[] )
{
	/* initialise Lua */
	L = lua_open();

	/* charge les librairies de base de Lua */
	luaL_openlibs(L);

	/* enregistre la fonction getFile dans la librairie Lua */
	lua_register(L, "getFile", getFile);

	/* execute le script */
	int executionError = luaL_dofile(L, "src/traqumoto.lua");
	if (executionError) {
		fprintf(stderr, "[TRM] Error trying to run `dofile(\"src/traqumoto.lua\")`\n");
	}

	/* ferme Lua */
	lua_close(L);

	return 0;
}
