{
  "nbformat": 4,
  "nbformat_minor": 0,
  "metadata": {
    "colab": {
      "provenance": [],
      "authorship_tag": "ABX9TyMV3WBfVpx4YxpOovBdtTiC",
      "include_colab_link": True
    },
    "kernelspec": {
      "name": "python3",
      "display_name": "Python 3"
    },
    "language_info": {
      "name": "python"
    }
  },
  "cells": [
    {
      "cell_type": "markdown",
      "metadata": {
        "id": "view-in-github",
        "colab_type": "text"
      },
      "source": [
        "<a href=\"https://colab.research.google.com/github/Harleneluyfook/WPS_System/blob/main/wps_mvp.py\" target=\"_parent\"><img src=\"https://colab.research.google.com/assets/colab-badge.svg\" alt=\"Open In Colab\"/></a>"
      ]
    },
    {
      "cell_type": "code",
      "source": [
        "with open(\"streamlit_app.py\", \"w\") as f:\n",
        "    f.write(\"\"\"\n",
        "import streamlit as st\n",
        "\n",
        "st.set_page_config(page_title=\"Test App\")\n",
        "\n",
        "st.title(\"Hello First Website 👋\")\n",
        "st.write(\"If you can see this, your Streamlit deployment works!\")\n",
        "\n",
        "if st.button(\"Click me\"):\n",
        "    st.success(\"It works 🎉\")\n",
        "\"\"\")"
      ],
      "metadata": {
        "id": "VsJHw7DA4tpG"
      },
      "execution_count": 7,
      "outputs": []
    }
  ]
}
