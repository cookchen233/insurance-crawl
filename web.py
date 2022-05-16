# coding=utf-8
import hashlib, inspect, re, time,os,json,sys,uuid,urllib,math,psutil,random,decimal
import streamlit as st


reload(sys)
sys.setdefaultencoding('utf8')

st.title('My first app')
st.write("Here's our first attempt at using data to create a table:")